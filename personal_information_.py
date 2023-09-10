from telegram import Update,ReplyKeyboardMarkup,ReplyKeyboardRemove,InlineKeyboardButton,InlineKeyboardMarkup
from telegram.ext import ConversationHandler,MessageHandler,CommandHandler,ApplicationBuilder,CallbackContext,ContextTypes,filters,CallbackQueryHandler
import requests
import json
from file_util import Document
from request_util import Request_to_Django 

personal_information = {
    "FullName":"",
    "UserRoll":"",
    "Street":"",
    "City":"",
    "Country":"",
    "SelfDescribtion":"",
    "BirthDate":"",
    "PhoneNumber":"",

}
STATE1,STATE2,STATE3,STATE4,STATE5,STATE6,STATE7,STATE8,STATE9 = range(9)
replay_keyboard = [
    [InlineKeyboardButton("edit personal_information",callback_data="update")],
]
markup = InlineKeyboardMarkup(replay_keyboard)
async def start(update:Update,context:ContextTypes.DEFAULT_TYPE)->int:
    await context.bot.send_message(chat_id=context._user_id,text="play with your personal information",reply_markup=markup)

    return STATE4 
# async def choose(update:Update,context:ContextTypes.DEFAULT_TYPE):
#     query = update.callback_query
#     data = query.data
    
    
#       #   request = Request_to_Django(endpoint="http://localhost:8000/api/personalinfo/",token=context.user_data["access_token"])
#       #   response = request.get_request()
#       #   if response.status_code !=404:
#       #       response_datas = response.json()
            
#             # keyboard = [[InlineKeyboardButton(value,callback_data=key["id"])] for response_data in response_datas]
#             # mark_up = InlineKeyboardMarkup(keyboard)
#             # await context.bot.send_message(chat_id=context._user_id,text="all experiance",reply_markup=mark_up)
           
            
                  
            
            
#     await context.bot.send_message(chat_id=context._user_id,text="no personal_information to be found")


   


async def to_be_updated(update:Update,context:ContextTypes.DEFAULT_TYPE)->int:
    query = update.callback_query
    data = query.data
    request = Request_to_Django(endpoint=f"http://localhost:8000/api/personalinfo",token=context.user_data["access_token"])
    response = request.get_request()
    data = response.json()
    filtered_data =  {key: value for key, value in data.items() if isinstance(value, str) }
    keyboard = [[InlineKeyboardButton(value,callback_data=key)] if type(value)!=list else [] for key, value in filtered_data.items()]
    mark_up = InlineKeyboardMarkup(keyboard)
    context.user_data["updated_personal_info"] = filtered_data
    await context.bot.send_message(chat_id=context._user_id,text="here we go",reply_markup=mark_up)
    return STATE5
    
async def handling_edited_button(update:Update,context:ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    userdata = context.user_data["updated_personal_info"][data]
    context.user_data["choiced_to_update_personal"]=data
    await context.bot.send_message(chat_id=context._user_id,text=userdata)
    return STATE6
async def update_handler(update:Update,context:ContextTypes.DEFAULT_TYPE):
    chosen = context.user_data["choiced_to_update_personal"]
    if update.message.text !=None:
        context.user_data["updated_personal_info"][chosen] = update.message.text
        return STATE5
async def save_data(update:Update,context:ContextTypes.DEFAULT_TYPE):
    user_date = context.user_data["updated_personal_info"]
    keyboard = [
        [InlineKeyboardButton("Save",callback_data="save")],[InlineKeyboardButton("Cancel",callback_data="cancel")]
    ]
    mark_up = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=context._user_id,text=f"""
her is you data {user_date}
""",reply_markup=mark_up)
    return STATE7
    
async def save_handler(update:Update,context:ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data_of_user= context.user_data["updated_personal_info"]
   
    data = query.data
    if data =="save":
        request = Request_to_Django(endpoint=f"http://localhost:8000/api/personalinfo",token=context.user_data["access_token"])
        response = request.put_request(data=data_of_user)
        await context.bot.send_message(chat_id=context._user_id,text=f"updated here is your data{response.json()}")
        return STATE1
    else:
        await context.bot.send_message(chat_id=context._user_id,text=f"OKEY")
        return STATE4





    

              
    
    

conversation_personalinfo = ConversationHandler(
    entry_points=[CommandHandler("Personal_info",start)],
    states={
        STATE4:[CallbackQueryHandler(to_be_updated)],
        STATE5:[CallbackQueryHandler(handling_edited_button),CommandHandler("done",save_data)],
        STATE6:[MessageHandler(filters.TEXT & ~filters.COMMAND,update_handler)],
        STATE7:[CallbackQueryHandler(save_handler)],
        
        

    },
    fallbacks=[]
)