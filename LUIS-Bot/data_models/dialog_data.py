'''
用來儲存新增訓練句子時的資料
'''

class DialogData:

    def __init__(
      self, 
      training_utterance: str = None, 
      specified_intent: str = None, 
      specified_entity: str = None, 
      tagged_entity: str = None, 
      isTraining: int = 0,
      luis_appid: str = None
      ):
        self.training_utterance = training_utterance
        self.specified_intent = specified_intent
        self.specified_entity = specified_entity
        self.tagged_entity = tagged_entity
        self.isTraining = isTraining
        
        self.luis_appid = luis_appid
