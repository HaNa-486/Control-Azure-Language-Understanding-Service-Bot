# LUIS Bot
## Brief introduction
Language Understanding service, aka LUIS, is one of the Azure Cognitive Service. Currently, users can control LUIS through [official website](https://www.luis.ai/home) or test/control the entire functions by Postman. 

I knew the fastest way to configure LUIS was importing a LUIS app, an JSON format template. However, I just wondered if there was a more convenient way to setup LUIS model and utilize this service so I built a bot with Microsoft Bot Framework to set up LUIS and , in the meantime, demonstrate an example usage of using this service.

This bot is able to help users manipulate the core setup of LUIS, including creating an LUIS app, creating an entity, creating an intent, creating utterances and labelling the entity values, train and publish. In addition, I add a function to let users check which LUIS app is being set up at that time. 

I have built a sample [messenger bot](m.me/105868227718666). If you want to test the bot, you can go for it. However, I strongly suggest you reproduce a bot of your own. This is the place where you can see the actual result. If you use my [messenger bot](m.me/105868227718666), You set up the LUIS app under my account. 
## To Reproduce
### Prerequisites
> An Azure Account with at least two Resource Group

> A Facebook Account

> Install Anaconda or [Miniconda (Python 3.7)](https://docs.conda.io/en/latest/miniconda.html "Miniconda下載頁面")

> Install [Bot Framework Emulator v4](https://github.com/Microsoft/BotFramework-Emulator/releases/tag/v4.7.0)

> Intsall Azure Command-Line Interface (CLI)
>> For [Windows User](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli-windows?view=azure-cli-latest "Windows的下載教學")
> 
>> For [Mac User](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli-macos?view=azure-cli-latest "Mac的下載教學")

> Install [Visual Studio Code(VS Code)](https://code.visualstudio.com/download "VScode下載頁面")
>> Install **Python extension** of VS Code
>
>> Install **Azure App Service Extension** of VS code

### Setup Environment

1.1 Open VS Code, click **File** in the upper left and select **Open Folder**
> Choose the folder named `LUIS-Bot`


1.2 Open a terminal in VS Code

1.3 Install the specified package
```powershell
pip install -r requirements.txt
```

### Setup Language Understanding Serive(LUIS)
2.1 Go to [LUIS.ai](https://www.luis.ai/home)

2.2 Sign in your Azure account

2.3 Click **Import new app**

2.4 Select `LUIS Bot App.json` and click **Done**

2.5 Go to the newly created app

2.6 Click **Train**

2.7 Click **Publish**

2.8 Select **Production** and click **Publish**

2.9 Click **Manage**

2.10 Copy `Application ID` to the clipboard

2.11 Click **Azure Resource**

2.12 Copy `Primary key` to the clipboard

### Test the Main Code
3.1 Go back to VS code and open `config.py`

3.2 Copy and paste the following varaiables
* LUIS_APP_ID : `<Application ID>`
* LUIS_API_KEY : `<Primary key>`

<p align = "center">
    <img src="./images/test main code1.jpg" width="65%">
</p>

3.3 Open a terminal and run the code 
```powershell
python app.py
```

3.4 Open `Bot Framework Emulator (V4)`

3.5 Click **Open Bot** and key in the following url and Click **Connect**
> `http://localhost:3978/api/messages`
<p align = "center">
    <img src="./images/test main code2.jpg" width="30%">
</p>

3.6 Type the following messages
> 妳好
> 
> ```The bot won't work```

> 我要創建一個服務叫做**點餐系統**
> 
> ```The bot will create a new LUIS app```

> 我要創建一個實體叫做**食物**
> 
> ```The bot will create a new entity for the newly created LUIS app```

> 我要創建一個意圖叫做**點餐**
> 
> ```The bot will create a new intent for the newly created LUIS app```

> 我要訓練句子
> 
> ```Start a new waterfall dialog for adding new uterances```


<p align = "center">
    <img src="./images/test main code3.jpg" width="50%">
</p>

<p align = "center">
    <img src="./images/test main code4.jpg" width="50%">
</p>

3.7 Enter the training utterance
> 我要吃蛋餅
> 
> ```Type a training utterances```

> 點餐
> 
> ```Specify the intent of the new utterance```

> 食物
> 
> ```Specify the entity showing in the new utterance```

> 蛋餅
> 
> ```Specify the tagged word```

> Yes
> 
> ```Reply Yes to prepare for the next round of add new utterances dialog```
> 
> No
> 
> ```Reply No to leave the dialog```

<p align = "center">
    <img src="./images/test main code5.jpg" width="50%">
</p>

<p align = "center">
    <img src="./images/test main code6.jpg" width="50%">
</p>

3.8 Repeat STEP 3.7 but change the utterance
```text
兩份薯條外帶
捲餅一份謝謝
我想要吃漢堡
我今天想喝珍奶
我想點一隻螃蟹
```

3.9 Go to [LUIS.ai](https://www.luis.ai/home) and check the LUIS app you just created through bot

3.10 Click **Build** and click the intent you just crerated through bot
<p align = "center">
    <img src="./images/test main code7.jpg" width="50%">
</p>

3.11 Check the result of utterances you just created through bot

3.12 Go back to `Bot Framework Emulator (V4)`

3.13 Type the following messages
> 我要訓練
> 
> ```The bot will start to train the LUIS app```

> 我要發行
> 
> ```The bot will pubilsh the LUIS app ```

<p align = "center">
    <img src="./images/test main code8.jpg" width="50%">
</p>

3.14 Go back to [LUIS.ai](https://www.luis.ai/home)

3.15 Check the app if trained and published or not
<p align = "center">
    <img src="./images/test main code9.jpg" width="50%">
</p>

### Deploy a Bot to App Service
4.1 Go to [Azure Portal](https://portal.azure.com/#home) and search the `Azure Active Directory`

4.2 Click **App registration** in the left blade

4.3 Click **New registration**

4.4 Key in the following blank and click **Register**
* Name : `<Any word>`
* Supported account types : `<The second option>`

4.5 Copy `Application ID` to the clipboard

4.6 Click **Certificates & secrets**

4.7 Click **+ New client secret**

4.8 Fill in the following blank and click **Add**
* Description : `<Any word>`
* Expires : `Never`

4.9 Copy the **Client secrets** `Value` to the clipboard

4.10 Open a command prompt(ex. Powershell) and key in the following command 
```powershell 
az login
```
4.11 Sign in the current used Azure Account

4.12 Navigate to the  folder `LUIS-Bot` directory

4.13 Key in the following command
> Warning : The Resource Group for LUIS service cannot be used here, otherwise, you will fail to create a Python-based App Service. Create another one !!
```powershell
az group deployment create --resource-group "<name-of-resource-group>" --template-file "template-with-preexisting-rg.json" --parameters appId="<app-id-from-previous-step>" appSecret="<password-from-previous-step>" botId="<id or bot-app-service-name>" newWebAppName="<bot-app-service-name>" existingAppServicePlan="<name-of-app-service-plan>" appServicePlanLocation="<region-location-name>"
```
4.14 Go back to the VS code window opened in STEP 3.1

4.15 Click Azure icon on the left side

4.16 (Not necessarily STEP) Click the **Sign in to Azure...** and key in the account and password to finish the login procedure
<p align = "center">
    <img src="./images/deploy bot1.jpg" width="20%">
</p>

4.17 Click the **blue icon** to start the deployment procedure

4.18 Select `LUIS-Bot`
<p align = "center">
    <img src="./images/deploy bot2.jpg" width="60%">
</p>

4.19 Select the web app you created
<p align = "center">
    <img src="./images/deploy bot3.jpg" width="60%">
</p>


4.20 After the deployment completed, go to [Azure Portal](https://portal.azure.com/#home) and search the `Bot Services`

4.21 Select the Bot you created 

4.22 Click **Test in Web Chat** and you will have the same testing experiences in `Bot Framework Emulator (V4)`

### Connect Bot with Facebook
5.1 Go to [Facebook page](https://www.facebook.com/bookmarks/pages)

5.2 Click **Create a Page**
<p align = "center">
    <img src="./images/sync with fb1.jpg" width="50%">
</p>

5.3 Select **Business or Brand**
<p align = "center">
    <img src="./images/sync with fb2.jpg" width="50%">
</p>

5.4 Fill in the blank
* Page Name : `<Any name>`
* Category : `Personal Blog`

5.5 Select **See more** ot the left section
<p align = "center">
    <img src="./images/sync with fb3.jpg" width="20%">
</p>

5.6 Click **About** and copy `Page ID` to the clipboard
<p align = "center">
    <img src="./images/sync with fb4.jpg" width="50%">
</p>

5.7 Go to [facebook for developers](https://developers.facebook.com/quickstarts/?platform=web)

5.8 Click **Skip and Create App ID**


5.9 Fill in the following blank and click **Create App ID**
* Display Name : `<Any name>`
* Contact Email : `<Any email you own>`

5.10 Click **Settings** and select **Basic**

5.11 Copy `APP ID` and `APP Secret` to the clipboard
<p align = "center">
    <img src="./images/sync with fb5.jpg" width="50%">
</p>

5.12 Select **Advanced**

5.13 Under Security section, find **Allow api Access to App Settings** and switch the option to `Yes` 

5.14 Select **Dashboard** on the top-left panel

5.15 Scroll down and find `Messenger` box

5.16 Click **Set Up**
<p align = "center">
    <img src="./images/sync with fb6.jpg" width="45%">
</p>

5.17 Under Access Token, click **Add or Remove Pages** 

5.18 Choose the page you created

5.19 Select **Generate Token**
<p align = "center">
    <img src="./images/sync with fb7.jpg" width="50%">
</p>

5.20 Check the box `I Understand` and click **Copy** and click **Done**

5.21 Go back to [Azure Portal]((https://portal.azure.com/#home))

5.22 Find the Bot Service you previously tested

5.23 Click **Channel** under Bot management section

5.24 Click **Facebook**

5.25 Fill in the following requirements and click **Save**
* Facebook App ID : `<The APP ID copied in STEP 5.11>`
* Facebok App Secret : `<The APP Secret copied in STEP 5.11>`
* Page ID : `<The Page ID copied in STEP 5.6>`
* Page Access Token : `<The token copied in STEP 5.20>`

5.26 Copy `Callback URL` and `Verify Token` for upcoming use

5.27 Go back to [facebook for developers](https://developers.facebook.com/quickstarts/?platform=web)

5.28 Click **Settings** under Messenger section

5.29 Under Webhooks section, Click **Add Callback URL**
<p align = "center">
    <img src="./images/sync with fb8.jpg" width="50%">
</p>

5.30 Paste the URL and Token copied in STEP 5.26

5.31 Click **Verify and Save**

5.32 Select **Add Subscription**
<p align = "center">
    <img src="./images/sync with fb9.jpg" width="50%">
</p>

5.33 Check the `messages` and click **Save**
<p align = "center">
    <img src="./images/sync with fb10.jpg" width="50%">
</p>

5.34 Use you own facebook account to test the bot

## Prosepct
So far, the bot is use one and only LUIS app to set up the other LUIS apps. We still can add a database for this bot to store different LUIS app ID for exchanging the LUIS app the bot originally used. 

Furthermore, the bot is not good enough to identify many intent & entity names. For doing so, we need to add another utterances as many as we could to train the original LUIS app. 