import base64
import logging
from pathlib import Path
from openai import OpenAI, OpenAIError

log = logging.getLogger(__name__)

class AiError(RuntimeError):
    pass


def ask_image(client: OpenAI, image_path: Path, prompt: str,
              *, model: str = "deepseek-flash", max_tokens: int = 600) -> str:
    """
    將一張圖片發個ai, 讓他返回回答的內容
    失敗(鉴权/超时/网络等)時openai 包自會拋出異常, 直接往上冒;
    """
    # (1) 轉base64
    with open(image_path, "rb") as fh:
        b64 = base64.b64encode(fh.read()).decode("utf-8")
    img_uri = f"data:image/png;base64,{b64}"

    # (2) 向AI 請求
    log.info(f"正在向{model} 發送請求")
    try:
        # noinspection PyTypeChecker
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": img_uri}},
                    ],
                }
            ],
            max_tokens=max_tokens,
        )
    except OpenAIError as exc:
        raise AiError(f"AI 發送信息失敗, 檢查API key 或模型等. 詳細信息: {exc}") from None

    # (3) 提取回答
    reply = (resp.choices[0].message.content or "").strip()
    if not reply:
        raise AiError("AI 回復內容為空, 請重試") # content 為空字串或None
    log.info(f"{model} 回答完畢")
    return reply

if __name__ == '__main__':
    client = OpenAI(
        api_key="sk-xxx",
        base_url="https://api.deepseek.com"
    )

    reply = ask_image(client=client, image_path=Path("./tmp/screen.png"), prompt="請辨識這張圖片中的文字, 將文字輸出. 然後在最後面回答答案, 以及你為什麼選擇這個答案")
    print(reply)