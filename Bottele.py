from telegram import Update
from telegram.ext import ConversationHandler,MessageHandler,CommandHandler,ApplicationBuilder,ContextTypes,filters
import requests
import json
from file_util import Document
from request_util import Request_to_Django 
from education import conversation_education
from experiance import conversation_experiance
from project import conversation_project
from personal_information_ import conversation_personalinfo
from skill import conversation_skill
import os
from dotenv import load_dotenv


load_dotenv()
TELEGRAM_API_TOKEN = os.getenv("TELEGRAM_API_TOKEN")
DEBUG = os.getenv("DEBUG") == "True"
STATE1,STATE2,STATE3,STATE4,STATE5 = range(5)
data ={
   "username":"",
   "password":"",
   "email":""
}
personal_info ={
   "FullName":"",
   "BirthDate":"",
   "UserRoll":"",
   "PhoneNumber":"",
   "PhoneNumber":"",
   "SelfDescribtion":"",
   "Street":"",
   "City":"",
   "Country":""
}
token = {
   "access_token":""
}
headers = {
    "Content-Type": "application/json"
}

async def start(update:Update,context:ContextTypes.DEFAULT_TYPE) ->int:
   print(context._user_id)
   print(update.message.from_user.username)
   await update.message.reply_text("can you enter your full name with space and email with the format like 'john legend/joni@gmail.com'")
   return STATE1
async def register_or_login(update:Update,context:ContextTypes.DEFAULT_TYPE) ->int:
   user_input =update.message.text.split("/")
   if len(user_input)!=2:
      await context.bot.send_message(chat_id=context._user_id,text="⚠️please send in the valid format it is invalid")
      return STATE1
   data['username'] = user_input[0].replace(" ","_")
   data['email'] = user_input[1]
   data['password']=context._user_id
   request_data = json.dumps(data)
   file = Document()
   if not file.read_to_check("list_of_user.txt",data["username"].replace("_"," ")):
      request = requests.post(url="http://localhost:8000/api/register/",data=request_data,headers=headers)
      if request.status_code == 201:
         token["access_token"]=request.json()["access_token"]
         context.user_data["access_token"] = request.json()["access_token"]
         await update.message.reply_text("""
can you tell me about yourself in the format like 
         birthday/job,phone number/self describtion/Street of where you live in / City of where you live/Country of where you live/
     eg:- 
      2000-07-11/Back-End Developer/0978513510/I'm good backend developer with good experience and i engaged in big projects/Bole/Adama/Ethiopiaa
""")   
         return STATE2
         
      else:
         await update.message.reply_text("error please try again ")
         return STATE1
   else:
       request = requests.post(url="http://localhost:8000/api/login/",data=request_data,headers=headers)
       if request.status_code == 200:
          token["access_token"]=request.json()["access_token"]
          context.user_data["access_token"] = request.json()["access_token"]
          await context.bot.send_message(chat_id=context._user_id,text="""
successfully logged in 
""")
          return ConversationHandler.END
       else:
          doc = Document()
          doc.delete_name("list_of_user.txt",data["username"].replace("_"," ")) 
          await context.bot.send_message(chat_id=context._user_id,text="please try again")
          return STATE1
   
   

async def personal_info_register(update:Update,context:ContextTypes.DEFAULT_TYPE):
   await context.bot.send_message(chat_id=context._user_id,text=update.message.text)
   user_data = update.message.text.split("/") 
   if len(user_data)!= 7:
       await context.bot.send_message(chat_id=context._user_id,text="⚠️please send in the valid format it is invalid or missed data please check")
       return STATE2
   personal_info["FullName"] = data["username"].replace("_"," ")
   personal_info["BirthDate"] = user_data[0]
   personal_info["UserRoll"] =user_data[1]
   personal_info["PhoneNumber"] = user_data[2]
   personal_info["SelfDescribtion"]= user_data[3]
   personal_info["Street"] = user_data[4]
   personal_info["City"] = user_data[5]
   personal_info["Country"] =user_data[6]
   personal_data = json.dumps(personal_info)
   requ = Request_to_Django(endpoint="http://localhost:8000/api/personalinfo/",token=token["access_token"])
   response = requ.post_request(data=personal_data)
   if response.status_code == 201:
      doc = Document()
      doc.write_into_file("list_of_user.txt",data["username"].replace("_"," ")+"\n")
      await context.bot.send_message(chat_id=context._user_id,text="""
successfully registered
""")
      return ConversationHandler.END
   else:
      await context.bot.send_message(chat_id=context._user_id,text=f"{response.json()}")
      return STATE2


  

async def create_education(update:Update,context:ContextTypes.DEFAULT_TYPE): 
   await context.bot.send_message(chat_id=context._user_id,text="please register first /start")
   



conversation_one = ConversationHandler(
   entry_points=[CommandHandler("start",start)],
   states={
      STATE1:[MessageHandler(~filters.COMMAND,register_or_login)],
      STATE2:[MessageHandler(~filters.COMMAND,personal_info_register)]
      

   },fallbacks=[]
) 

app = ApplicationBuilder().token(TELEGRAM_API_TOKEN).build()

app.add_handler(conversation_one)
app.add_handlers([CommandHandler("create_education",create_education)])
app.add_handlers([conversation_education])
app.add_handlers([conversation_experiance])
app.add_handlers([conversation_personalinfo])
app.add_handlers([conversation_project])
app.add_handlers([conversation_skill])
app.run_polling()