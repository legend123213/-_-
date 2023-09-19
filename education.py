from telegram import Update,ReplyKeyboardMarkup,ReplyKeyboardRemove,InlineKeyboardButton,InlineKeyboardMarkup
from telegram.ext import ConversationHandler,MessageHandler,CommandHandler,ApplicationBuilder,CallbackContext,ContextTypes,filters,CallbackQueryHandler
import requests
import json
from file_util import Document
from request_util import Request_to_Django 

experience = {
    "NameOfSchool":"",
    "CertifiedWith":"",
    "Street":"",
    "City":"",
    "Country":"",
    "DescribtionOfWork":"",
    "DateFrom":"",
    "DateTo":"",

}
STATE1,STATE2,STATE3,STATE4,STATE5,STATE6,STATE7,STATE8,STATE9,STATE10 = range(10)
replay_keyboard = [
    [InlineKeyboardButton("add experience",callback_data="create")],[InlineKeyboardButton("edit experience",callback_data="update")],[InlineKeyboardButton("view existing experience",callback_data="view")],[InlineKeyboardButton("delete experience",callback_data="delete")]
]
markup = InlineKeyboardMarkup(replay_keyboard)
async def start(update:Update,context:ContextTypes.DEFAULT_TYPE)->int:
    await context.bot.send_message(chat_id=context._user_id,text="play with your education",reply_markup=markup)

    return STATE1
async def choose(update:Update,context:ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    if data == "create":
        await context.bot.send_message(chat_id=context._user_id,text="""ok let preside please insert your education status and all previous educations information with this format name of the school/type of Cerifcate you get start /start date for the of the school you started/the date you complited/what you study and describtion/street of the school /city of the school/Country of the school  
      eg:-
               St.Theresa High School/Diploma/2016-01-01/2020-01-01/Dipo/Dire Dawa/Ethiopia/i learned in local private high school and i particapate in social service and club in my high school  """)
        return STATE2
    elif data == "view" or data == "update" or data =="delete":
        request = Request_to_Django(endpoint="http://localhost:8000/api/personal/educations/",token=context.user_data["access_token"])
        response = request.get_request()
        response_datas = response.json()
        keyboard = [[InlineKeyboardButton(response_data["NameOfSchool"],callback_data=response_data["id"])] for response_data in response_datas]
        mark_up = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(chat_id=context._user_id,text="all experiance",reply_markup=mark_up)
        if data == "view":
            return STATE3
        elif data == "update":
            return STATE4
        
        else:
            return STATE8


   
async def create(update:Update,context:ContextTypes.DEFAULT_TYPE):
    user_data = update.message.text.split("/")
    experience["NameOfSchool"]=user_data[0]
    experience["CertifiedWith"]=user_data[1]
    experience["DateFrom"]=user_data[2]
    experience["DateTo"]=user_data[3] if user_data[3] not in ['none','None'] else None
    experience["Street"]=user_data[4]
    experience["City"]=user_data[5]
    experience["Country"]=user_data[6]
    experience["DescribtionOfWork"]=user_data[7]
    request = Request_to_Django(endpoint="http://localhost:8000/api/personal/educations/",token=context.user_data["access_token"])
    response = request.post_request(experience)
    if not response:
        await context.bot.send_message(chat_id=context._user_id,text="add succufully")
        await context.bot.send_message(chat_id=context._user_id,text="play with your education",reply_markup=markup)
        return STATE1
    else:
      await context.bot.send_message(chat_id=context._user_id,text=response.json())
      return STATE1
async def view_experiance(update:Update,context:ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    request = Request_to_Django(endpoint=f"http://localhost:8000/api/personal/education/{data}",token=context.user_data["access_token"])
    response = request.get_request()
    
    await context.bot.send_message(chat_id=context._user_id,text=response.json())
    return STATE3
async def to_be_updated(update:Update,context:ContextTypes.DEFAULT_TYPE)->int:
    query = update.callback_query
    data = query.data
    request = Request_to_Django(endpoint=f"http://localhost:8000/api/personal/education/{data}",token=context.user_data["access_token"])
    response = request.get_request()
    data = response.json()

    keyboard = [[InlineKeyboardButton(text="Education Information",callback_data="info")],
                [InlineKeyboardButton(text="Education Place Address ",callback_data="address")],
                [InlineKeyboardButton(text="Education Date",callback_data="date")]]
    mark_up = InlineKeyboardMarkup(keyboard)
    context.user_data["updated_experiance"] = data
    await context.bot.send_message(chat_id=context._user_id,text="here we go",reply_markup=mark_up)
    return STATE10
    
async def handling_edited_button(update:Update,context:ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    userdata = context.user_data["updated_experiance"][data]
    context.user_data["choiced_to_update"]=data
    await context.bot.send_message(chat_id=context._user_id,text=userdata)
    return STATE6
async def update_handler(update:Update,context:ContextTypes.DEFAULT_TYPE):
    chosen = context.user_data["choiced_to_update"]
    if update.message.text !=None:
        context.user_data["updated_experiance"][chosen] = update.message.text
    if update.message.text == "no" and chosen =="DateTo":
        context.user_data["updated_experiance"][chosen] = None
    return STATE5
async def save_data(update:Update,context:ContextTypes.DEFAULT_TYPE):
    user_date = context.user_data["updated_experiance"]
    keyboard = [
        [InlineKeyboardButton("Save",callback_data="save")],[InlineKeyboardButton("Cancel",callback_data="cancel")]
    ]
    mark_up = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=context._user_id,text=f"""
here is the data that update
Name of the school : {user_date['NameOfSchool']}
high achievement : {user_date['CertifiedWith']}
about the experiance : {user_date['DescribtionOfWork']}
starting date : {user_date['DateFrom']}
finished date : {user_date['DateTo']}
""",reply_markup=mark_up)
    return STATE7
    
async def save_handler(update:Update,context:ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data_of_user= context.user_data["updated_experiance"]
    pk = str(data_of_user["id"])
    data = query.data
    if data =="save":
        request = Request_to_Django(endpoint=f"http://localhost:8000/api/personal/education/{pk}",token=context.user_data["access_token"])
        response = request.put_request(data=data_of_user)
        await context.bot.send_message(chat_id=context._user_id,text=f"your data is updated")
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
        endpoint = f"http://localhost:8000/api/personal/education/{pk}" if pk !="all"  else f"http://localhost:8000/api/personal/educations/" 
        request= Request_to_Django(endpoint=endpoint,token=context.user_data["access_token"])
        response = request.delete_request()
        if response.status_code == 200:
            await context.bot.send_message(chat_id=context._user_id,text=response.json['message'])
            return STATE8
        else:
            await context.bot.send_message(chat_id=context._user_id,text="something wrong please try again!")
            return STATE1
    else:
        return STATE1


    

async def chosen_to_update(update:Update,context:ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    user_experiance = context.user_data["updated_experiance"]
    if data == "info":
        keyboard = [[InlineKeyboardButton(text="School Name",callback_data="NameOfSchool"),InlineKeyboardButton(text="Ceritified with ",callback_data="CertifiedWith"),InlineKeyboardButton(text="about what you study",callback_data="DescribtionOfWork")]]
        mark_up = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(chat_id=context._user_id,text=f"""
School name -------> {user_experiance["NameOfSchool"]}
Certified by  Company ------->{user_experiance["CertifiedWith"]}
Description of the about the study --------->{user_experiance["DescribtionOfWork"]}

""",reply_markup=mark_up)
    elif data == "address":
        keyboard = [[InlineKeyboardButton(text="Street",callback_data="Street"),InlineKeyboardButton(text="City",callback_data="City"),InlineKeyboardButton(text="Country",callback_data="Country")]]
        mark_up = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(chat_id=context._user_id,text=f"""
Address of the Education Center -------> {user_experiance["Street"]},{user_experiance["City"]},{user_experiance["Country"]}
""",reply_markup=mark_up)
    else:
        keyboard = [[InlineKeyboardButton(text="Starting day",callback_data="DateFrom"),InlineKeyboardButton(text="Ended day",callback_data="DateTo")]]

        mark_up = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(chat_id=context._user_id,text=f"""
Starting / Ending date with Company -------> {user_experiance["DateFrom"]}/{user_experiance["DateTo"]}
""",reply_markup=mark_up)
    return STATE5





    

              
    
    

conversation_education = ConversationHandler(
    entry_points=[CommandHandler("Education",start)],
    states={
        STATE1:[CallbackQueryHandler(choose)],
        STATE2:[MessageHandler(filters.TEXT & ~filters.COMMAND,create)],
        STATE3:[CallbackQueryHandler(view_experiance)],
        STATE4:[CallbackQueryHandler(to_be_updated)],
        STATE5:[CallbackQueryHandler(handling_edited_button),CommandHandler("done",save_data)],
        STATE6:[MessageHandler(filters.TEXT & ~filters.COMMAND,update_handler)],
        STATE7:[CallbackQueryHandler(save_handler)],
        STATE8:[CallbackQueryHandler(delete_handler)],
        STATE9:[CallbackQueryHandler(final_delete_handle)],
        STATE10:[CallbackQueryHandler(chosen_to_update)]
        

    },
    fallbacks=[]
)