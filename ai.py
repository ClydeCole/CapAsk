# ----------------------------------------------------------------------
# AI 修改請注意!
# 為了兼容Termux 可能無法安裝OpenAI 的python 庫,
# 因此決定讓AI 直接修改文件, 讓代碼直接使用python 自帶的urllib庫.
#
# adb 連接電腦方式測試 可成功運行, 但未經過嚴格審查, 可能存在BUG.
# 圖片以base64 直接內嵌請求中, 不需要先上傳檔案取得file_id.
# ----------------------------------------------------------------------

import base64
import json
import logging
import sys
from pathlib import Path
from urllib import error, request

BASE_DIR = Path(__file__).resolve().parent

log = logging.getLogger(__name__)

class AiError(RuntimeError):
    pass

class AiAsk:
    def __init__(self, cfg: dict):
        ai_cfg = cfg.get("ai", {})

        self.api_key = ai_cfg.get("api_key", "")
        self.base_url = ai_cfg.get("base_url", "https://api.deepseek.com").rstrip("/")
        self.model = ai_cfg.get("model", "deepseek-flash")
        self.max_tokens = int(ai_cfg.get("max_tokens", 2000))
        self.timeout = int(ai_cfg.get("timeout", 60))
        self.system_prompt = ai_cfg.get("system_prompt", "")
        log.info("初始化AI完畢")

    # 使用標準庫 urllib 呼叫 OpenAI 相容 API, 不需要安裝 openai 庫
    def _headers(self):
        return {
            "Authorization": f"Bearer {self.api_key}",
        }

    def _post_json(self, url, data):
        req = request.Request(
            url,
            data=json.dumps(data).encode("utf-8"),
            headers={**self._headers(), "Content-Type": "application/json"},
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=self.timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except (error.URLError, TimeoutError) as e:
            raise AiError("AI 請求發送失敗, 請檢查你的網路或者API KEY") from e

    def image(self):
        # 直接讀取二進制並發送
        log.info(f"將圖片上傳{self.model}...")
        with open(BASE_DIR / "tmp" / "screen.png", "rb") as f:
            b64_image = base64.b64encode(f.read()).decode("utf-8")

        log.info(f"等待{self.model} 的回復")
        # 發送對話
        resp = self._post_json(f"{self.base_url}/chat/completions", {
            "model": self.model,
            "messages": [
                {"role": "system", "content": self.system_prompt},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{b64_image}",
                            },
                        }
                    ],
                },
            ],
            "max_tokens": self.max_tokens,
        })
        return resp["choices"][0]["message"]["content"]

if __name__ == '__main__':
    import yaml
    logging.basicConfig(level=logging.INFO, stream=sys.stdout, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    with open(BASE_DIR / "config.yaml", "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    AiAsk(cfg).image()