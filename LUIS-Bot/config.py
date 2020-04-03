import os

class DefaultConfig:
    """ Bot Configuration """

    PORT = 3978
    APP_ID = os.environ.get("MicrosoftAppId", "")
    APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "")

    # (需修改) 此ID為創建新LUIS APP的所使用的辨識LUIS APP ID
    LUIS_APP_ID = os.environ.get("LuisAppId", "c5ee17cc-2474-4aed-9bf6-f0ae9eedc025")
    # (需修改) 此KEY為Azure Portal上LUIS Service的KEY
    LUIS_API_KEY = os.environ.get("LuisAPIKey", "d0988067b416476aa79a875616748a64")
    # (可修改) 依照LUIS Service創建地區而變更
    LUIS_API_HOST_NAME = os.environ.get("LuisAPIHostName", "westus.api.cognitive.microsoft.com")
    # (可修改) 創建luis服務時，需要用到的變數
    LUIS_APP_VERSION_ID = '0.1'