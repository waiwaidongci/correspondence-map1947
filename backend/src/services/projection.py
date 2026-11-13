import numpy as np
from fastapi import HTTPException
from src.models import CorrespondenceRun
from src.constants.enums import RunStatus
from .catalog import table_data
from .fingerprint import fingerprint
from .audit import record

TOL = 1e-12


def _axis_bundle(result, axis):
    """Return own active categories, the OPPOSITE-set reference masses and the
    rank-first projection factor. A supplementary row profile is defined over
    columns and compared with column marginals via V; the column case is the
    symmetric row-marginal/U analogue."""
    if axis == 'row':
        return (result['row_categories'],
                np.asarray(result['column_masses'], dtype=float),
                np.asarray(result['svd']['Vt'], dtype=float))
    return (result['column_categories'],
            np.asarray(result['row_masses'], dtype=float),
            np.asarray(result['svd']['U'], dtype=float).T)


def project_one(counts, ref_masses, factors, shown):
    """Project one supplementary profile onto the fixed reference axes.

    From S V = U Sigma, active principal coordinates are
    F = D_r^-1/2 U Sigma = (P-rc^T) D_c^-1/2 V; a supplementary row profile
    therefore projects as z^T V with z = D_c^-1/2 (p_tilde - c), and the
    column analogue is g^T U. No singular-value division: dividing again would
    leave the null-space-near axes undefined and mis-scale every coordinate.
    Returns (point_dict, None) on success or (None, reason) when invalid.
    """
    total = float(sum(counts))
    if total <= 0:
        return None, '补充类别计数总和为零：零边际没有可定义的轮廓，不能投影（参考分析的零边际类别亦被剔除）。'
    x = np.asarray(counts, dtype=float)
    profile = x / total
    # Standardized profile against the opposite-set reference marginals.
    z = (profile - ref_masses) / np.sqrt(ref_masses)
    rank = factors.shape[0]
    # factors are already sliced to the numerical rank: the full SVD may retain
    # null-space singular vectors (sigma ~= 0), which never define an axis.
    full_coordinates = z @ factors.T
    shown = min(shown, rank)
    coordinates = full_coordinates[:shown]
    distance_sq = float(np.sum(((profile - ref_masses) ** 2) / ref_masses))
    if distance_sq <= TOL * TOL:
        cos2 = [None] * rank
        display_quality = None
        centroid = True
    else:
        cos2 = (full_coordinates ** 2 / distance_sq).tolist()
        display_quality = float(np.clip(sum(cos2[:shown]), 0.0, 1.0))
        centroid = False
    return {
        'coordinates': coordinates.tolist(),
        'full_coordinates': full_coordinates.tolist(),
        'cos2': cos2,
        'display_quality': display_quality,
        'chi_square_distance_squared': distance_sq,
        'centroid': centroid,
        'supplementary': True,
        'contributions': [],
    }, None


def project_supplementary(db, data, user):
    run = db.get(CorrespondenceRun, data.run_id)
    if not run:
        raise HTTPException(404, '对应分析不存在')
    if run.status != RunStatus.SUCCEEDED or not run.result or not run.result.get('direction_available'):
        raise HTTPException(422, '参考分析未成功或没有可解释方向，无法投影补充点')

    study, rows, cols, cells, table = table_data(db, run.study_id)
    current_fp = fingerprint(study, rows, cols, cells, run.axes)
    if current_fp != run.result.get('fingerprint'):
        record(db, user.email, 'projection.stale_rejected', {'run_id': run.id})
        raise HTTPException(409, '源数据已变化：参考分析指纹与当前研究不一致，投影依据已失效。请先用当前数据重新运行分析，再投影补充类别，避免沿用过期轴与惯量。')

    result = run.result
    rank = result['rank']
    dropped = {'row': result.get('dropped_rows', []), 'column': result.get('dropped_columns', [])}
    projected_points = []

    for axis, incoming in (('row', data.rows), ('column', data.columns)):
        active_categories, ref_masses, factors = _axis_bundle(result, axis)
        factors = factors[:rank]
        active_codes = {c['code'] for c in active_categories}
        dropped_codes = {c['code'] for c in dropped[axis]}
        # The point set being projected sits on this axis; its counts are read
        # against the opposite axis, whose active codes define valid columns.
        opposite = result['column_categories'] if axis == 'row' else result['row_categories']
        opposite_codes = [c['code'] for c in opposite]
        seen = set()
        for item in incoming:
            base = {'axis': axis, 'code': item.code, 'label': item.label, 'supplementary': True,
                    'status': 'rejected', 'reason': None, 'missing_codes': [],
                    'supplementary_total': None, 'mass': None,
                    'coordinates': [], 'full_coordinates': [], 'cos2': [],
                    'display_quality': None, 'chi_square_distance_squared': None,
                    'centroid': None, 'contributions': []}
            if item.code in seen:
                base['reason'] = '本次提交中该轴内 code 重复，补充类别无法唯一匹配。'
                projected_points.append(base)
                continue
            seen.add(item.code)
            if item.code in active_codes:
                base['reason'] = f'code {item.code} 已存在于参考分析的有效{"行" if axis=="row" else "列"}类别：它属于活动点，混入原表会重算轴与惯量；补充投影仅接受新类别。'
                projected_points.append(base)
                continue
            if item.code in dropped_codes:
                base['reason'] = f'code {item.code} 在参考分析中因零边际被剔除：没有可用轮廓，不能作为补充点投影。'
                projected_points.append(base)
                continue
            unknown = [code for code in item.counts if code not in opposite_codes]
            if unknown:
                base['reason'] = '存在无法匹配对侧活动类别的 code：' + '、'.join(unknown) + '。补充计数按 code 匹配，请改用参考分析中的对侧类别 code。'
                projected_points.append(base)
                continue
            ordered = [int(item.counts.get(code, 0)) for code in opposite_codes]
            missing_codes = [code for code in opposite_codes if code not in item.counts]
            point, reason = project_one(ordered, ref_masses, factors,
                                        result['displayed_axes'])
            if reason:
                base['reason'] = reason
                base['missing_codes'] = missing_codes
                projected_points.append(base)
                continue
            base.update(point)
            base['status'] = 'projected'
            base['missing_codes'] = missing_codes
            # Supplementary points carry no reference mass: the table mass
            # structure is fixed by the reference run, so expose only the
            # submitted total for verification, never an artificial r_i/c_j.
            base['supplementary_total'] = sum(ordered)
            base['mass'] = None
            projected_points.append(base)

    if not projected_points:
        raise HTTPException(422, '未提供任何补充行或补充列')

    payload = {
        'run_id': run.id,
        'reference_fingerprint': result['fingerprint'],
        'current_fingerprint': current_fp,
        'reference_stale': False,
        'reference_n': result['n'],
        'reference_total_inertia': result['total_inertia'],
        'reference_displayed_axes': result['displayed_axes'],
        'reference_axes': result['axes'],
        'projected_points': projected_points,
        'projection_note': '补充（illustrative）点按固定参考轴投影：参考点、奇异值、惯量与独立性诊断保持不变；补充点不参与轴贡献，其质量为显示轴 cos²，质心处 cos² 无定义。两集仍为主坐标几何，跨集距离不可直接比较。',
    }
    record(db, user.email, 'projection.created', {
        'run_id': run.id,
        'projected': sum(1 for p in projected_points if p['status'] == 'projected'),
        'rejected': sum(1 for p in projected_points if p['status'] == 'rejected'),
    })
    return payload
