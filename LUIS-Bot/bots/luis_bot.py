from botbuilder.ai.luis import LuisApplication, LuisRecognizer, LuisPredictionOptions
from botbuilder.core import ActivityHandler, TurnContext, RecognizerResult, ConversationState, UserState
from botbuilder.schema import ChannelAccount
from botbuilder.dialogs import Dialog
from helpers.dialog_helper import DialogHelper

from config import DefaultConfig
from data_models import DialogData

import json
import requests

class LuisBot(ActivityHandler):
    def __init__(
        self, 
        config: DefaultConfig, 
        conversation_state: ConversationState, 
        user_state: UserState, 
        dialog: Dialog
        ):
        luis_application = LuisApplication(
            config.LUIS_APP_ID, 
            config.LUIS_API_KEY, 
            "https://" + config.LUIS_API_HOST_NAME
            )
        luis_options = LuisPredictionOptions(include_all_intents=True, include_instance_data=True)
        self.recognizer = LuisRecognizer(luis_application, luis_options, True)

        self.subscription_key = config.LUIS_API_KEY
        self.version_id = config.LUIS_APP_VERSION_ID
        # 可空白或直接填寫一個現有的luis app，不過需要注意其version_id是否與config.py裡的一樣
        self.luis_appid = ''              
        
        # 激活dialog_data.py裡的資訊
        self.user_profile_accessor = user_state.create_property("DialogData")

        if conversation_state is None:
            raise TypeError("[DialogBot]: Missing parameter. conversation_state is required but None was given")
        if user_state is None:
            raise TypeError("[DialogBot]: Missing parameter. user_state is required but None was given")
        if dialog is None:
            raise Exception("[DialogBot]: Missing parameter. dialog is required")
        self.conversation_state = conversation_state
        self.user_state = user_state
        self.dialog = dialog
    
    async def on_turn(self, turn_context: TurnContext):
        await super().on_turn(turn_context)
        # Save any state changes that might have ocurred during the turn.
        await self.conversation_state.save_changes(turn_context)
        await self.user_state.save_changes(turn_context)

    # 首次加入的問候的訊息
    async def on_members_added_activity(self, members_added: [ChannelAccount], turn_context: TurnContext):
        for member in members_added:
            if member.id != turn_context.activity.recipient.id:
                await turn_context.send_activity(
                    f"歡迎來到自動創建LUIS APP的機器人，請說出你的需求")

    # 每一次對話都是由這裏來處理
    async def on_message_activity(self, turn_context: TurnContext):
        # 要使用共用的data時，需先下這行指令
        user_profile = await self.user_profile_accessor.get(
            turn_context, 
            DialogData
            )
        # 將要被自動化新增的LUIS APP ID寫進dialog_data裡
        user_profile.luis_appid = self.luis_appid

        # 判斷是否為新增訓練語句的對話框，如果是，則進入；如不是，則開始辨識要做的動作
        if user_profile.isTraining == 1 :
            await DialogHelper.run_dialog(self.dialog, turn_context, self.conversation_state.create_property("DialogState"))
        else:            
            # 辨識使用者傳的訊息
            recognizer_result = await self.recognizer.recognize(turn_context)
            # 找出最高可能的意圖
            intent = LuisRecognizer.top_intent(recognizer_result)

            # 針對每個意圖做出不同的動作
            if intent == "創建一個新的LUIS_APP" :
                app_name = recognizer_result.entities['app_name'][0]
                await self.create_luis_app(app_name, turn_context)  
            elif intent == "創建一個entity" : 
                entity_name = recognizer_result.entities['entity_name'][0]
                await self.create_luis_entity(entity_name, turn_context)
            elif intent == "創建一個intent" : 
                intent_name = recognizer_result.entities['intent_name'][0]
                await self.create_luis_intent(intent_name, turn_context)
            elif intent == "新增訓練語句" : 
                await DialogHelper.run_dialog(self.dialog, turn_context, self.conversation_state.create_property("DialogState"))
                # 當判斷出為「新增訓練語句」的意圖，更改flag，使其下次直接進入用來新增訓練語句的對話框
                user_profile.isTraining  = 1
            elif intent == "訓練LUIS_APP" : 
                await self.train_luis(turn_context)
            elif intent == "PUBLISH_LUIS_APP" : 
                await self.publish_luis(turn_context)
            elif intent == "確認在哪一個LUIS_APP" : 
                await self.check_luis_app_name(turn_context)
            else : 
                await turn_context.send_activity(f"luis無法辨識")

    # 創建新的LUIS APP
    async def create_luis_app(self, App_Name, turn_context: TurnContext) :
        try:
            app_name = App_Name   
            #語系在這裡選擇，中文只有zh-cn
            culture = "zh-cn"
            create_app_dict = {
                "name": app_name,     
                "description": "LUIS生成LUIS",
                "culture": culture ,
                "initialVersionId": self.version_id
            }
            create_app_body = json.dumps(create_app_dict)
            await self.create_app(create_app_body, turn_context)
        except : 
            await turn_context.send_activity(f"有出錯，請檢查明後再試試看")
    async def create_app(self, body, turn_context:TurnContext):
        headers = {
            # Request headers
            'Content-Type': 'application/json',
            'Ocp-Apim-Subscription-Key': self.subscription_key
        }
        url = "https://westus.api.cognitive.microsoft.com/luis/api/v2.0/apps/"
        response = requests.request("POST", url, data=body, headers=headers)
        response_txt = json.loads(response.text)                                 #要換成txt格式，不然之後的appid格式會是錯的
        self.luis_appid = response_txt                                           # 當創造新的luis app 時，需要更新當前操作的luis appid
        await turn_context.send_activity(f"完成新增服務的執行續，產生出的luis appid為{response_txt}")
    
    # 創建新的Entity
    async def create_luis_entity(self, Entity_Name, turn_context:TurnContext):
        try :
            example_entity_name = Entity_Name   
            create_entity_dict = {
                "name" : example_entity_name
            }
            create_entity_body1 = json.dumps(create_entity_dict)
            await self.add_entity(create_entity_body1, turn_context)
        except : 
            await turn_context.send_activity(f"有出錯，請檢查明後再試試看")
    async def add_entity(self, body, turn_context:TurnContext):
        headers = {
            # Request headers
            'Content-Type': 'application/json',
            'Ocp-Apim-Subscription-Key': self.subscription_key
        }
        url = "https://westus.api.cognitive.microsoft.com/luis/api/v2.0/apps/{}/versions/{}/entities".format(self.luis_appid, self.version_id)
        response = requests.request("POST", url, data=body, headers=headers)
        response_txt = json.loads(response.text) 
        await turn_context.send_activity(f"成功完成一個執行緒(entity)，回傳訊息為{response_txt}")
    
    # 創建新的Intent
    async def create_luis_intent(self, Intent_Name, turn_context:TurnContext):
        try : 
            example_intent_name = Intent_Name  
            create_intent_dict = {
                "name" : example_intent_name
            }
            create_intent_body = json.dumps(create_intent_dict)
            await self.add_intent(create_intent_body, turn_context)
        except : 
            await turn_context.send_activity(f"有出錯，請檢查明後再試試看")
    async def add_intent(self, body, turn_context:TurnContext):
        headers = {
            # Request headers
            'Content-Type': 'application/json',
            'Ocp-Apim-Subscription-Key': self.subscription_key
        }
        url = "https://westus.api.cognitive.microsoft.com/luis/api/v2.0/apps/{}/versions/{}/intents".format(self.luis_appid, self.version_id)
        response = requests.request("POST", url, data=body, headers=headers)
        response_txt = json.loads(response.text) 
        await turn_context.send_activity(f"成功完成一個執行緒(intent)，回傳訊息為{response_txt}")
    
    # 訓練LUIS APP
    async def train_luis(self, turn_context:TurnContext):
        headers = {
            # Request headers
            'Ocp-Apim-Subscription-Key': self.subscription_key
        }
        url = "https://westus.api.cognitive.microsoft.com/luis/api/v2.0/apps/{}/versions/{}/train".format(self.luis_appid, self.version_id)
        response = requests.request("POST", url, headers=headers)
        response_txt = json.loads(response.text) 
        await turn_context.send_activity(f"成功開始訓練一個LUIS APP，回傳訊息為{response_txt['status']}")
    
    # Publish當下正在操控的LUIS APP
    async def publish_luis(self, turn_context:TurnContext):
        publish_app_dict = {
            "versionId": self.version_id,
            "isStaging": 'false',   
            "directVersionPublish": 'false'    
        }
        publish_app_json = json.dumps(publish_app_dict)
        await self.publish_app(publish_app_json, turn_context)  
    async def publish_app(self, body, turn_context:TurnContext):
        headers = {
            # Request headers
            'Content-Type': 'application/json',
            'Ocp-Apim-Subscription-Key': self.subscription_key
        }
        url = "https://westus.api.cognitive.microsoft.com/luis/api/v2.0/apps/{}/publish".format(self.luis_appid)
        response = requests.request("POST", url, data=body, headers=headers)
        response_txt = json.loads(response.text)
        #如果只要單純查看網址，請使用 response_txt['endpointUrl']
        await turn_context.send_activity(f"成功publish一個LUIS APP，詳細資料為{response_txt}")
    
    # 確認當前正在操控的LUIS APP的名稱
    async def check_luis_app_name(self, turn_context:TurnContext):
        headers = {
            # Request headers
            'Ocp-Apim-Subscription-Key': self.subscription_key
        }
        url = "https://westus.api.cognitive.microsoft.com/luis/api/v2.0/apps/{}".format(self.luis_appid)
        response = requests.request("GET", url, headers=headers)
        response_txt = json.loads(response.text) 
        await turn_context.send_activity(f"目前所訓練的LUIS APP為 {response_txt['name']}")
