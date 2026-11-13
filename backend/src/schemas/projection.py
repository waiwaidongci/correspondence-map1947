from pydantic import BaseModel, Field, StrictInt, model_validator


class SupplementaryPointInput(BaseModel):
    code: str = Field(min_length=1, max_length=30)
    label: str = Field(min_length=1, max_length=80)
    # Counts keyed by the opposite axis' active category code; missing codes
    # are treated as zero at projection and reported back for verification.
    counts: dict[str, StrictInt] = Field(min_length=1, max_length=12)

    @model_validator(mode='after')
    def check_counts(self):
        bad = [k for k, v in self.counts.items() if not 0 <= v <= 1000000]
        if bad:
            raise ValueError('补充计数须为0..1000000的非负整数')
        return self


class ProjectionInput(BaseModel):
    run_id: int = Field(gt=0)
    rows: list[SupplementaryPointInput] = Field(default=[], max_length=12)
    columns: list[SupplementaryPointInput] = Field(default=[], max_length=12)

    @model_validator(mode='after')
    def check_non_empty_and_unique(self):
        if not self.rows and not self.columns:
            raise ValueError('至少提供一个补充行或补充列')
        for axis, items in (('row', self.rows), ('column', self.columns)):
            codes = [x.code for x in items]
            if len(codes) != len(set(codes)):
                raise ValueError(f'补充{"行" if axis == "row" else "列"}类别 code 不得重复')
        return self
