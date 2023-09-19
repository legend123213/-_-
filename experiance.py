from telegram import Update,ReplyKeyboardMarkup,ReplyKeyboardRemove,InlineKeyboardButton,InlineKeyboardMarkup
from telegram.ext import ConversationHandler,MessageHandler,CommandHandler,ApplicationBuilder,CallbackContext,ContextTypes,filters,CallbackQueryHandler
import requests
import json
from file_util import Document
from request_util import Request_to_Django 

experience = {
    "NameOfCompany":"",
    "Role":"",
    "Street":"",
    "City":"",
    "Country":"",
    "DescribtionOfWork":"",
    "DateFrom":"",
    "DateTo":"",

}

STATE1,STATE2,STATE3,STATE4,STATE5,STATE6,STATE7,STATE8,STATE9,STATE10,STATE11,STATE12 = range(12)
replay_keyboard = [
    [InlineKeyboardButton("add experience",callback_data="create")],[InlineKeyboardButton("edit experience",callback_data="update")],[InlineKeyboardButton("view existing experience",callback_data="view")],[InlineKeyboardButton("delete experience",callback_data="delete")]
]
markup = InlineKeyboardMarkup(replay_keyboard)
async def start(update:Update,context:ContextTypes.DEFAULT_TYPE)->int:
    await context.bot.send_message(chat_id=context._user_id,text="play with your experiance",reply_markup=markup)

    return STATE1
async def choose(update:Update,context:ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    if data == "create":
        await context.bot.send_message(chat_id=context._user_id,text="""ok let preside please insert your experiance status and all previous experiances information with this format name of the company/type of work you get  /date that you start working in company/the date you completed or resign from the company/what you role in company and descriptions/street of the company /city of the company/Country of the company  
      eg:-
               Backos company/Backend dev/2016-01-01/2020-01-01/Mebrate/Adama/Ethiopia/i worked in the company as backend developer in Django framework of python i had good experience in their""")
        return STATE2
    elif data == "view" or data == "update" or data =="delete":
        request = Request_to_Django(endpoint="http://localhost:8000/api/personal/experiances/",token=context.user_data["access_token"])
        response = request.get_request()
        if response.status_code !=404:
            response_datas = response.json()
            
            keyboard = [[InlineKeyboardButton(response_data["NameOfCompany"],callback_data=response_data["id"])] for response_data in response_datas]
            mark_up = InlineKeyboardMarkup(keyboard)
            await context.bot.send_message(chat_id=context._user_id,text="all experiance",reply_markup=mark_up)
            if data == "view":
                  return STATE3
            elif data == "update":
                  return STATE4
            
            else:
                  return STATE8
        else:
            await context.bot.send_message(chat_id=context._user_id,text="no experience to be found")


   
async def create(update:Update,context:ContextTypes.DEFAULT_TYPE):
    user_data = update.message.text.split("/")
    experience["NameOfCompany"]=user_data[0]
    experience["Role"]=user_data[1]
    experience["DateFrom"]=user_data[2]
    experience["DateTo"]=user_data[3]
    experience["Street"]=user_data[4]
    experience["City"]=user_data[5]
    experience["Country"]=user_data[6]
    experience["DescribtionOfWork"]=user_data[7]
    request = Request_to_Django(endpoint="http://localhost:8000/api/personal/experiances/",token=context.user_data["access_token"])
    response = request.post_request(experience)
    if not response:
        await context.bot.send_message(chat_id=context._user_id,text="add succufully")
        await context.bot.send_message(chat_id=context._user_id,text="play with your experiance",reply_markup=markup)
        return STATE1
    else:
      await context.bot.send_message(chat_id=context._user_id,text=response.json())
      return STATE1
async def view_experiance(update:Update,context:ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    request = Request_to_Django(endpoint=f"http://localhost:8000/api/personal/experiance/{data}",token=context.user_data["access_token"])
    response = request.get_request()
    
    await context.bot.send_message(chat_id=context._user_id,text=response.json())
    return STATE3
async def to_be_updated(update:Update,context:ContextTypes.DEFAULT_TYPE)->int:
    query = update.callback_query
    data = query.data
    request = Request_to_Django(endpoint=f"http://localhost:8000/api/personal/experiance/{data}",token=context.user_data["access_token"])
    response = request.get_request()
    data = response.json()
    # keyboard = [[InlineKeyboardButton(value,callback_data=key)] for key, value in data.items()]
    # mark_up = InlineKeyboardMarkup(keyboard)
    keyboard = [[InlineKeyboardButton(text="Experience Information",callback_data="info")],
                [InlineKeyboardButton(text="Experience Place Address ",callback_data="address")],
                [InlineKeyboardButton(text="Experience Date",callback_data="date")]]
    mark_up = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=context._user_id,text="hello there you can now update the experience",reply_markup=mark_up)
    context.user_data["updated_experiance"] = data
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
        return STATE5
async def save_data(update:Update,context:ContextTypes.DEFAULT_TYPE):
    user_date = context.user_data["updated_experiance"]
    keyboard = [
        [InlineKeyboardButton("Save",callback_data="save")],[InlineKeyboardButton("Cancel",callback_data="cancel")]
    ]
    mark_up = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=context._user_id,text=f"""
here is the data that update
Name of the company : {user_date['NameOfCompany']}
role you working on : {user_date['Role']}
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
        request = Request_to_Django(endpoint=f"http://localhost:8000/api/personal/experiance/{pk}/",token=context.user_data["access_token"])
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
        endpoint = f"http://localhost:8000/api/personal/experiance/{pk}" if pk !="all"  else f"http://localhost:8000/api/personal/experiances/" 
        request= Request_to_Django(endpoint=endpoint,token=context.user_data["access_token"])
        response = request.delete_request()
        if response:
            await context.bot.send_message(chat_id=context._user_id,text="Done")
            return STATE1
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
        keyboard = [[InlineKeyboardButton(text="School Name",callback_data="NameOfSchool"),InlineKeyboardButton(text="Role",callback_data="CertifiedWith"),InlineKeyboardButton(text="about what you study",callback_data="DescribtionOfWork")]]
        mark_up = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(chat_id=context._user_id,text=f"""
Company name -------> {user_experiance["NameOfCompany"]}
role in the  Company ------->{user_experiance["Role"]}
Description of the about the experience --------->{user_experiance["DescribtionOfWork"]}

""",reply_markup=mark_up)
    elif data == "address":
        keyboard = [[InlineKeyboardButton(text="Street",callback_data="Street"),InlineKeyboardButton(text="City",callback_data="City"),InlineKeyboardButton(text="Country",callback_data="Country")]]
        mark_up = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(chat_id=context._user_id,text=f"""
Address of the Company -------> {user_experiance["Street"]},{user_experiance["City"]},{user_experiance["Country"]}
""",reply_markup=mark_up)
    else:
        keyboard = [[InlineKeyboardButton(text="Starting day",callback_data="DateFrom"),InlineKeyboardButton(text="Ended day",callback_data="DateTo")]]

        mark_up = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(chat_id=context._user_id,text=f"""
Starting / Ending date with Company -------> {user_experiance["DateFrom"]}/{user_experiance["DateTo"]}
""",reply_markup=mark_up)

    

    
    
    return STATE5









    

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
             
    
    

conversation_experiance = ConversationHandler(
    entry_points=[CommandHandler("Experience",start)],
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
    fallbacks=[CommandHandler('back',back_to)]
)