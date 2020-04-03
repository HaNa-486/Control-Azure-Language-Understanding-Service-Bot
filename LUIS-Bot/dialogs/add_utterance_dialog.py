from botbuilder.dialogs import (
    ComponentDialog,
    WaterfallDialog,
    WaterfallStepContext,
    DialogTurnResult
)
from botbuilder.dialogs.prompts import (
    TextPrompt,
    ConfirmPrompt,
    PromptOptions
)
from botbuilder.dialogs.choices import Choice
from botbuilder.core import MessageFactory, UserState

from data_models import DialogData
from config import DefaultConfig

import json
import requests


class AddUtteranceDialog(ComponentDialog):
    def __init__(self, user_state: UserState):
        super(AddUtteranceDialog, self).__init__(AddUtteranceDialog.__name__)

        self.user_profile_accessor = user_state.create_property("DialogData")
        
        ### add_dialog --> 增加來回對話的round
        self.add_dialog(
            WaterfallDialog(
                WaterfallDialog.__name__,
                [
                    self.enter_a_training_utterance,
                    self.enter_the_specified_intent,
                    self.enter_the_specified_entity,
                    self.enter_the_tagged_entity,
                    self.inquire_keep_going_or_not,
                    self.final_step
                ]
            )
        )
        #依照本次dialog對話需要的方法，增加方法(yes/no問題、選項問題、純文字題等等)
        self.add_dialog(TextPrompt(TextPrompt.__name__))
        self.add_dialog(ConfirmPrompt(ConfirmPrompt.__name__))
        
    #依照每次要問的問題，各自設定一個function
    async def enter_a_training_utterance(self, step_context:WaterfallStepContext) -> DialogTurnResult :
        return await step_context.prompt(TextPrompt.__name__, PromptOptions(prompt=MessageFactory.text("請輸入要訓練的句子")))
 
    async def enter_the_specified_intent(self, step_context:WaterfallStepContext) -> DialogTurnResult :
        step_context.values["utterance"] = step_context.result
        return await step_context.prompt(TextPrompt.__name__, PromptOptions(prompt=MessageFactory.text("請輸入要加入到哪一個意圖")))

    async def enter_the_specified_entity(self, step_context:WaterfallStepContext) -> DialogTurnResult :
        step_context.values["intent"] = step_context.result
        return await step_context.prompt(TextPrompt.__name__, PromptOptions(prompt=MessageFactory.text("請輸入要用哪個實體標記")))
        
    async def enter_the_tagged_entity(self, step_context:WaterfallStepContext) -> DialogTurnResult :
        step_context.values["entity"] = step_context.result
        return await step_context.prompt(TextPrompt.__name__, PromptOptions(prompt=MessageFactory.text("請輸入要被標記實體")))
        
    async def inquire_keep_going_or_not(self, step_context:WaterfallStepContext) -> DialogTurnResult :
        step_context.values["words"] = step_context.result
        return await step_context.prompt(ConfirmPrompt.__name__, PromptOptions(prompt=MessageFactory.text("是否要繼續加入訓練句子?")))

    async def final_step(self, step_context:WaterfallStepContext) -> DialogTurnResult :
        user_profile = await self.user_profile_accessor.get(step_context.context, DialogData)
        ####### 這邊開始針對之前得到的答案，一一寫入最後的總結
        user_profile.training_utterance = step_context.values["utterance"]
        user_profile.specified_intent = step_context.values["intent"]
        user_profile.specified_entity = step_context.values["entity"]
        user_profile.tagged_entity = step_context.values["words"]
        #計算要標記entity的index值
        start_index = user_profile.training_utterance.find(user_profile.tagged_entity)
        end_index = start_index + len(user_profile.tagged_entity) - 1
        #新增Dict
        create_utterance_dict = {
            "text": user_profile.training_utterance,
            "intentName": user_profile.specified_intent,
            "entityLabels":
            [
                {
                    "entityName": user_profile.specified_entity,
                    "startCharIndex": start_index,
                    "endCharIndex": end_index
                }
            ]
        }
        create_utterance_body = json.dumps(create_utterance_dict)
        response = self.add_batch_utterance(user_profile.luis_appid, create_utterance_body)
        await step_context.context.send_activity(f"完成新增訓練語句的執行續，詳細資料為{response}")
        #依照使用者回答的Yes/No問題，確定是否要繼續增加訓練句子
        if step_context.result :
            user_profile.isTraining = 1
            await step_context.context.send_activity("我們將會留在加入訓練句子的流程，請先輸入任一字元以繼續")
        else :
            user_profile.isTraining = 0
            await step_context.context.send_activity("我們將跳出加入訓練句子的流程，請直接輸入你想要做的事情")
        #一定要有這個做收尾，因為每一個dialog要以下一個dialog為終點，或是以結束為終點
        return await step_context.end_dialog()
    
    #luis增加訓練語句的function
    def add_batch_utterance(self, appid, body):
        headers = {
            # Request headers
            'Content-Type': 'application/json',
            'Ocp-Apim-Subscription-Key': DefaultConfig.LUIS_API_KEY
        }
        url = "https://westus.api.cognitive.microsoft.com/luis/api/v2.0/apps/{}/versions/{}/example".format(appid, DefaultConfig.LUIS_APP_VERSION_ID)
        response = requests.request("POST", url, data=body, headers=headers)
        return response.text

