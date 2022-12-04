import json
import pandas as pd


class StockIndexInfoParser:
    def __init__(self, fname):
        self.fname = fname
        self._table = None
        self.parse()

    def parse(self):
        with open(self.fname) as fp:
            self._data = json.loads(fp.read())

        df = pd.DataFrame(self._data["results"])

        def _(dfx):
            indexes = dfx["indexes"].str.split(",").explode()
            return pd.DataFrame(
                {
                    "company": dfx["company"],
                    "spotlight": dfx["spotlight"],
                    "code": dfx["code"],
                    "indexes": indexes,
                }
            )

        dfr = (
            df.groupby(["company", "spotlight", "code"]
                       ).apply(_).reset_index(drop=True)
        )

        dfr["refdate"] = self._data["header"]["update"]
        dfr["duration_start_month"] = self._data["header"]["startMonth"]
        dfr["duration_end_month"] = self._data["header"]["endMonth"]
        dfr["duration_year"] = self._data["header"]["year"]

        dfr = dfr.rename(
            columns={
                "company": "corporation_name",
                "spotlight": "specification_code",
                "code": "symbol",
            }
        )

        self._table = dfr

    @property
    def data(self):
        return self._table
