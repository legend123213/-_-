from telegram import Update,ReplyKeyboardMarkup,ReplyKeyboardRemove,InlineKeyboardButton,InlineKeyboardMarkup
from telegram.ext import ConversationHandler,MessageHandler,CommandHandler,CallbackContext,ContextTypes,filters,CallbackQueryHandler
from request_util import Request_to_Django 

skill = {
    "language":"",
    "Rate":"",
  
}
STATE1,STATE2,STATE3,STATE4,STATE5,STATE6,STATE7,STATE8,STATE9 = range(9)
replay_keyboard = [
    [InlineKeyboardButton("add skill",callback_data="create")],[InlineKeyboardButton("edit skill",callback_data="update")],[InlineKeyboardButton("view existing skill",callback_data="view")],[InlineKeyboardButton("delete skill",callback_data="delete")]
]
markup = InlineKeyboardMarkup(replay_keyboard)
async def start(update:Update,context:ContextTypes.DEFAULT_TYPE)->int:
    await context.bot.send_message(chat_id=context._user_id,text="play with your skill",reply_markup=markup)

    return STATE1
async def choose(update:Update,context:ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    if data == "create":
        await context.bot.send_message(chat_id=context._user_id,text="""ok let preside please insert your skill that you work on and all previous skill information with this format name of the skill name/Rate upto 10 about the skill you know 
      eg:-
               Python/9""")
        return STATE2
    elif data == "view" or data == "update" or data =="delete":
        request = Request_to_Django(endpoint="http://localhost:8000/api/personal/skills/",token=context.user_data["access_token"])
        response = request.get_request()
        if response.status_code !=404:
            response_datas = response.json()
            
            keyboard = [[InlineKeyboardButton(response_data["language"],callback_data=response_data["id"])] for response_data in response_datas]
            mark_up = InlineKeyboardMarkup(keyboard)
            await context.bot.send_message(chat_id=context._user_id,text="all skills",reply_markup=mark_up)
            if data == "view":
                  return STATE3
            elif data == "update":
                  return STATE4
            
            else:
                  return STATE8
        else:
            await context.bot.send_message(chat_id=context._user_id,text="no skill to be found")


 
async def create(update:Update,context:ContextTypes.DEFAULT_TYPE):
    user_data = update.message.text.split("/")
    skill["language"]=user_data[0]
    skill["Rate"]=user_data[1]
    
    request = Request_to_Django(endpoint="http://localhost:8000/api/personal/skills/",token=context.user_data["access_token"])
    response = request.post_request(skill)
    if not response:
        await context.bot.send_message(chat_id=context._user_id,text="add succufully")
        await context.bot.send_message(chat_id=context._user_id,text="play with your skill",reply_markup=markup)
        return STATE1
    else:
      await context.bot.send_message(chat_id=context._user_id,text=response.json())
      return STATE1
async def view_experiance(update:Update,context:ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    request = Request_to_Django(endpoint=f"http://localhost:8000/api/personal/skill/{data}",token=context.user_data["access_token"])
    response = request.get_request()
    
    await context.bot.send_message(chat_id=context._user_id,text=response.json())
    return STATE3
async def to_be_updated(update:Update,context:ContextTypes.DEFAULT_TYPE)->int:
    query = update.callback_query
    data = query.data
    request = Request_to_Django(endpoint=f"http://localhost:8000/api/personal/skill/{data}",token=context.user_data["access_token"])
    response = request.get_request()
    data = response.json()

    keyboard = [[InlineKeyboardButton(data['Rate'],callback_data="Rate")]]
    mark_up = InlineKeyboardMarkup(keyboard)
    context.user_data["updated_skill"] = data
    await context.bot.send_message(chat_id=context._user_id,text="Edit your skill level ",reply_markup=mark_up)
    return STATE5
    
async def handling_edited_button(update:Update,context:ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    userdata = context.user_data["updated_skill"][data]
    context.user_data["choiced_to_update_"]=data
    await context.bot.send_message(chat_id=context._user_id,text=userdata)
    return STATE6
async def update_handler(update:Update,context:ContextTypes.DEFAULT_TYPE):
    chosen = context.user_data["choiced_to_update_"]
    if update.message.text !=None:
        context.user_data["updated_skill"][chosen] = update.message.text
        return STATE5
async def save_data(update:Update,context:ContextTypes.DEFAULT_TYPE):
    user_date = context.user_data["updated_skill"]
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
    data_of_user= context.user_data["updated_skill"]
    pk = str(data_of_user["id"])
    data = query.data
    if data =="save":
        request = Request_to_Django(endpoint=f"http://localhost:8000/api/personal/skill/{pk}",token=context.user_data["access_token"])
        response = request.put_request(data=data_of_user)
        await context.bot.send_message(chat_id=context._user_id,text=f"updated here is your data{response.json()}")
        return STATE1
    else:
        await context.bot.send_message(chat_id=context._user_id,text=f"OKEY")
        return STATE4
async def delete_handler(update:Update,context:ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    context.user_data["delete_id"] = query.data
    keyboard = [
        [InlineKeyboardButton("sure delete",callback_data="delete"),InlineKeyboardButton("no! cancel",callback_data="cancel")]
    ]
    mark_up = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id= context._user_id,text="are you sure you want to delete ",reply_markup=mark_up)
    return STATE9
async def final_delete_handle(update:Update,context:ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    if data == "delete":
        pk = str(context.user_data["delete_id"])
        endpoint = f"http://localhost:8000/api/personal/skill/{pk}" if pk !="all"  else f"http://localhost:8000/api/personal/skills/" 
        request= Request_to_Django(endpoint=endpoint,token=context.user_data["access_token"])
        response = request.delete_request()
        if response:
            await context.bot.send_message(chat_id=context._user_id,text=response.json['message'])
            return STATE8
        else:
            await context.bot.send_message(chat_id=context._user_id,text="something wrong please try again!")
            return STATE1
    else:
        return STATE1


    








    

              
    
    

conversation_skill = ConversationHandler(
    entry_points=[CommandHandler("skill",start)],
    states={
        STATE1:[CallbackQueryHandler(choose)],
        STATE2:[MessageHandler(filters.TEXT & ~filters.COMMAND,create)],
        STATE3:[CallbackQueryHandler(view_experiance)],
        STATE4:[CallbackQueryHandler(to_be_updated)],
        STATE5:[CallbackQueryHandler(handling_edited_button),CommandHandler("done",save_data)],
        STATE6:[MessageHandler(filters.TEXT & ~filters.COMMAND,update_handler)],
        STATE7:[CallbackQueryHandler(save_handler)],
        STATE8:[CallbackQueryHandler(delete_handler)],
        STATE9:[CallbackQueryHandler(final_delete_handle)]
        

    },
    fallbacks=[]
)