from typing import Union

import orjson


class ConfigHandler:
    def __init__(self, fn: str) -> None:
        self.fn: str = fn
        self.config: dict
        self.refresh()

    def refresh(self):
        with open(self.fn) as f:
            self.config = orjson.loads(f.read())

    def update(self, key: Union[dict, str], value: Union[dict, str, int, list]) -> None:
        self.config[key] = value
        with open(self.fn, "w") as f:
            f.write(str(orjson.dumps(self.config)))

    def get(self, key: Union[str, dict], default=None) -> Union[dict, str, int, list]:
        self.refresh()
        return self.config.get(key, default)
