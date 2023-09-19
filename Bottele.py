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
from resume import conversation
import os
from io import BytesIO
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
      2000-07-11/Back-End Developer/0978513510/I'm good backend developer with good experience and i engaged in big projects/Bole/Adama/Ethiopia
""")     
         
         return STATE2
         
      else:
         request = requests.post(url="http://localhost:8000/api/login/",data=request_data,headers=headers)
         if request.status_code == 200:
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
            context.bot.send_message(chat_id=context._user_id,text="something error please restart")
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
   requ = Request_to_Django(endpoint="http://localhost:8000/api/personalinfo/",token=token["access_token"])
   response = requ.post_request(data=personal_info)
   if not response:
      await context.bot.send_message(chat_id=context._user_id,text="""
successfully registered
""")  
      doc = Document()
      doc.write_into_file("list_of_user.txt",data["username"].replace("_"," ")+"\n")
      return ConversationHandler.END
   else:
      await context.bot.send_message(chat_id=context._user_id,text=f"{response.json()}")
      return STATE2


  

async def create_education(update:Update,context:ContextTypes.DEFAULT_TYPE): 
   await context.bot.send_message(chat_id=context._user_id,text="please register first /start")
   
async def back_to(update:Update,context:ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    current_state = context.user_data.get(user_id, {}).get('conversation_state')

    if current_state is not None:
        previous_state = None
        if current_state == STATE2:
            previous_state = STATE1
        elif current_state == STATE3:
            previous_state = STATE2

        if previous_state is not None:
            # Update the user's conversation state
            context.user_data[user_id]['conversation_state'] = previous_state

            # Handle state-specific actions for going back
            if previous_state == STATE1:
                update.message.reply_text("You are going back to State 1.")
            elif previous_state == STATE2:
                update.message.reply_text("You are going back to State 2.")

            return previous_state

    update.message.reply_text("You cannot go back from here.")
    return current_state  # Return the current state if the user cannot go back

async def resume(update:Update,context:ContextTypes.DEFAULT_TYPE):
   request = Request_to_Django(endpoint="http://localhost:8000/api/personal/resume/download",token=context.user_data["access_token"])
   response = request.get_request()
   await context.bot.send_document(chat_id=context._user_id,document=BytesIO(response.content),filename="your_resume.pdf")


conversation_one = ConversationHandler(
   entry_points=[CommandHandler("start",start)],
   states={
      STATE1:[MessageHandler(~filters.COMMAND,register_or_login)],
      STATE2:[MessageHandler(~filters.COMMAND,personal_info_register)]
      

   },fallbacks=[CommandHandler('back',back_to)]
) 

app = ApplicationBuilder().token(TELEGRAM_API_TOKEN).build()

app.add_handler(conversation_one)
app.add_handlers([CommandHandler("create_education",create_education)])
#app.add_handlers([CommandHandler("resume",resume)])
app.add_handlers([conversation_education])
app.add_handler(conversation)
app.add_handlers([conversation_experiance])
app.add_handlers([conversation_personalinfo])
app.add_handlers([conversation_project])
app.add_handlers([conversation_skill])
app.run_polling()