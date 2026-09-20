import logging
import sys
from pathlib import Path
from openai import OpenAI

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
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
        )
        log.info("初始化AI完畢")

    def image(self):
        # 直接讀取二進制並發送
        log.info(f"將圖片上傳{self.model}...")
        with open(BASE_DIR / "tmp" / "screen.png", "rb") as f:
            file_obj = self.client.files.create(
                file=f,
                purpose="user_data"
            )
        log.info(f"上傳成功, file_id: {file_obj.id}")

        log.info(f"等待{self.model} 的回復")
        # 發送對話
        # noinspection PyTypeChecker
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "file",
                            "file_id": file_obj.id,
                        }
                    ],
                },
            ],
            max_tokens=self.max_tokens,
            timeout=self.timeout,
        )
        print(resp)
        print("\n=====\n")
        print(resp.choices[0].message.content)

if __name__ == '__main__':
    import yaml
    logging.basicConfig(level=logging.INFO, stream=sys.stdout, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    with open(BASE_DIR / "config.yaml", "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    AiAsk(cfg).image()