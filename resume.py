from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ConversationHandler,
    CommandHandler,
    ContextTypes,
    CallbackQueryHandler,
)
from request_util import Request_to_Django

STATE1, STATE2, STATE3, STATE4, STATE5, STATE6, STATE7, STATE8 = range(8)


async def start_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['experience_set'] =[]
    context.user_data['education_set'] = []
    context.user_data['project_set'] = []
    context.user_data['skill_set'] = []

    keyboard = [[InlineKeyboardButton('choose the data',callback_data='choose')]]
    reply_mark = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=context._user_id,text="press button ",reply_markup=reply_mark)
    return STATE1
async def button(update:Update,context:ContextTypes.DEFAULT_TYPE):
    
    keyboard = [
        [InlineKeyboardButton("Experiance", callback_data="experience")],
        [InlineKeyboardButton("Education", callback_data="education")],
        [InlineKeyboardButton("Projects", callback_data="project")],
        [InlineKeyboardButton("Skills", callback_data="skill")],
        [InlineKeyboardButton("Language", callback_data="language")],
        [InlineKeyboardButton("Done", callback_data="done")],
    ]
    reply_mark = InlineKeyboardMarkup(keyboard)
    request = Request_to_Django(
        endpoint="http://localhost:8000/api/personalinfo/",
        token=context.user_data["access_token"],
    )
    response = request.get_request()
    context.user_data["all_user_data_for_template"] = response.json()
    await context.bot.send_message(
        chat_id=context._user_id,
        text="choose the your data to display in your resume if you do not want to choose or done choosing press done button",
        reply_markup=reply_mark,
    )
    return STATE2


async def choosing_the_from_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    data = data.split(" ")[0]
    if data == "experience":
        keyboard = [
            [
                InlineKeyboardButton(
                    response_data["NameOfCompany"]+ " selected", callback_data="experience " +str(response_data["id"])
                )
            ]
            if response_data["id"] in context.user_data['experience_set']
            else [
                InlineKeyboardButton(
                    response_data["NameOfCompany"],
                    callback_data="experience "+ str(response_data["id"]),
                )
            ]
            for response_data in context.user_data["all_user_data_for_template"][
                "experience_set"
            ]
            
        ]
        keyboard.append([InlineKeyboardButton('Done',callback_data='done')])
        reply_mark = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(
            chat_id=context._user_id,
            text="select the experiance",
            reply_markup=reply_mark,
        )
        
        
        return STATE3
    elif data == "education":
        query = update.callback_query
    data = query.data
    data = data.split(" ")[0]
    if data == "education":
        keyboard = [
            [
                InlineKeyboardButton(
                    response_data["NameOfSchool"]+ " selected", callback_data="experience " +str(response_data["id"])
                )
            ]
            if response_data["id"] in context.user_data['experience_set']
            else [
                InlineKeyboardButton(
                    response_data["NameOfSchool"],
                    callback_data="experience "+ str(response_data["id"]),
                )
            ]
            for response_data in context.user_data["all_user_data_for_template"][
                "education_set"
            ]
            
        ]
        keyboard.append([InlineKeyboardButton('Done',callback_data='done')])
        reply_mark = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(
            chat_id=context._user_id,
            text="select the your education",
            reply_markup=reply_mark,
        )
        
        
        return STATE4
    elif data == "project":
        keyboard = [
            [
                InlineKeyboardButton(
                    response_data["NameOfProject"]+ " selected", callback_data="project " +str(response_data["id"])
                )
            ]
            if response_data["id"] in context.user_data['project_set']
            else [
                InlineKeyboardButton(
                    response_data["NameOfProject"],
                    callback_data="project "+ str(response_data["id"]),
                )
            ]
            for response_data in context.user_data["all_user_data_for_template"][
                "project_set"
            ]
            
        ]
        keyboard.append([InlineKeyboardButton('Done',callback_data='done')])
        reply_mark = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(
            chat_id=context._user_id,
            text="select the your project",
            reply_markup=reply_mark,
        )
        
        
        return STATE5
    elif data == "skill":
        keyboard = [
            [
                InlineKeyboardButton(
                    response_data["language"]+ " selected", callback_data="skill " +str(response_data["id"])
                )
            ]
            if response_data["id"] in context.user_data['skill_set']
            else [
                InlineKeyboardButton(
                    response_data["language"],
                    callback_data="skill "+ str(response_data["id"]),
                )
            ]
            for response_data in context.user_data["all_user_data_for_template"][
                "skill_set"
            ]
            
        ]
        keyboard.append([InlineKeyboardButton('Done',callback_data='done')])
        reply_mark = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(
            chat_id=context._user_id,
            text="select the your skill to display on cv",
            reply_markup=reply_mark,
        )
        
        
        return STATE6
    elif data == "language":
        return STATE6
    else:
        return STATE2


async def choose_experiance(update: Update, context: ContextTypes.DEFAULT_TYPE):
        
        query = update.callback_query
        data = query.data
        id  = data.split(" ")[0] if len(data.split(" "))==1 else data.split(" ")[1]
        if id == "done":
            btn = [[InlineKeyboardButton(text='Continue',callback_data='d')]]
            replay = InlineKeyboardMarkup(btn)
            await context.bot.send_message(chat_id=context._user_id,text='choose another data',reply_markup=replay)
            return STATE1

        elif str(id) in context.user_data['experience_set']:
            context.user_data['experience_set'].remove(int(id))
        elif str(id) not in context.user_data['experience_set']:
            context.user_data['experience_set'].append(int(id)) 
            
        keyboard = [
            [
                InlineKeyboardButton(
                    response_data["NameOfCompany"]+ " selected", callback_data="experience " +str(response_data["id"])
                )
            ]
            if str(response_data["id"]) in context.user_data['experience_set']
            else [
                InlineKeyboardButton(
                    response_data["NameOfCompany"],
                    callback_data="experience "+ str(response_data["id"]),
                )
            ]
            for response_data in context.user_data["all_user_data_for_template"][
                "experience_set"
            ]
            
        ]
        keyboard.append([InlineKeyboardButton('Done',callback_data='done')])
        reply_mark = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(
            chat_id=context._user_id,
            text="select the experiance",
            reply_markup=reply_mark,
        )
        
       
        selected = context.user_data['experience_set']
        await context.bot.send_message(chat_id=context._user_id, text=f"""your selected data is {selected}""")
        return STATE3
            
async def choose_education(update:Update,context:ContextTypes.DEFAULT_TYPE):
            query = update.callback_query
            data = query.data
            id  = data.split(" ")[0] if len(data.split(" "))==1 else data.split(" ")[1]
            if id == "done":
                btn = [[InlineKeyboardButton(text='Continue',callback_data='d')]]
                replay = InlineKeyboardMarkup(btn)
                await context.bot.send_message(chat_id=context._user_id,text='choose another data',reply_markup=replay)
                return STATE1

            elif str(id) in context.user_data['education_set']:
                context.user_data['education_set'].remove(int(id))
            elif str(id) not in context.user_data['education_set']:
                context.user_data['education_set'].append(int(id)) 
                
            keyboard = [
                [
                    InlineKeyboardButton(
                        response_data["NameOfSchool"]+ " selected", callback_data="education " +str(response_data["id"])
                    )
                ]
                if str(response_data["id"]) in context.user_data['education_set']
                else [
                    InlineKeyboardButton(
                        response_data["NameOfSchool"],
                        callback_data="experience "+ str(response_data["id"]),
                    )
                ]
                for response_data in context.user_data["all_user_data_for_template"][
                    "education_set"
                ]
                
            ]
            keyboard.append([InlineKeyboardButton('Done',callback_data='done')])
            reply_mark = InlineKeyboardMarkup(keyboard)
            await context.bot.send_message(
                chat_id=context._user_id,
                text="select the your educations",
                reply_markup=reply_mark,
            )
            
        
            selected = context.user_data['education_set']
            await context.bot.send_message(chat_id=context._user_id, text=f"""your selected data is {selected}""")
            return STATE4

async def choose_project(update:Update,context:ContextTypes.DEFAULT_TYPE):
                query = update.callback_query
                data = query.data
                id  = data.split(" ")[0] if len(data.split(" "))==1 else data.split(" ")[1]
                if id == "done":
                    btn = [[InlineKeyboardButton(text='Continue',callback_data='d')]]
                    replay = InlineKeyboardMarkup(btn)
                    await context.bot.send_message(chat_id=context._user_id,text='choose another data',reply_markup=replay)
                    return STATE1

                elif str(id) in context.user_data['project_set']:
                    context.user_data['project_set'].remove(int(id))
                elif str(id) not in context.user_data['project_set']:
                    context.user_data['project_set'].append(int(id)) 
                    
                keyboard = [
                    [
                        InlineKeyboardButton(
                            response_data["NameOfProject"]+ " selected", callback_data="project " +str(response_data["id"])
                        )
                    ]
                    if str(response_data["id"]) in context.user_data['project_set']
                    else [
                        InlineKeyboardButton(
                            response_data["NameOfProject"],
                            callback_data="project "+ str(response_data["id"]),
                        )
                    ]
                    for response_data in context.user_data["all_user_data_for_template"][
                        "project_set"
                    ]
                    
                ]
                keyboard.append([InlineKeyboardButton('Done',callback_data='done')])
                reply_mark = InlineKeyboardMarkup(keyboard)
                await context.bot.send_message(
                    chat_id=context._user_id,
                    text="select the your project",
                    reply_markup=reply_mark,
                )
                
            
                selected = context.user_data['project_set']
                await context.bot.send_message(chat_id=context._user_id, text=f"""your selected data is {selected}""")
                return STATE5
async def choose_skill(update:Update,context:ContextTypes.DEFAULT_TYPE):
                query = update.callback_query
                data = query.data
                id  = data.split(" ")[0] if len(data.split(" "))==1 else data.split(" ")[1]
                if id == "done":
                    btn = [[InlineKeyboardButton(text='Continue',callback_data='d')]]
                    replay = InlineKeyboardMarkup(btn)
                    await context.bot.send_message(chat_id=context._user_id,text='choose another data',reply_markup=replay)
                    return STATE1

                elif str(id) in context.user_data['skill_set']:
                    context.user_data['skill_set'].remove(int(id))
                elif str(id) not in context.user_data['skill_set']:
                    context.user_data['skill_set'].append(int(id)) 
                    
                keyboard = [
                    [
                        InlineKeyboardButton(
                            response_data["language"]+ " selected", callback_data="skill " +str(response_data["id"])
                        )
                    ]
                    if response_data["id"] in context.user_data['skill_set']
                    else [
                        InlineKeyboardButton(
                            response_data["language"],
                            callback_data="skill "+ str(response_data["id"]),
                        )
                    ]
                    for response_data in context.user_data["all_user_data_for_template"][
                        "skill_set"
                    ]
                    
                ]
                keyboard.append([InlineKeyboardButton('Done',callback_data='done')])
                reply_mark = InlineKeyboardMarkup(keyboard)
                await context.bot.send_message(
                    chat_id=context._user_id,
                    text="select the your skill to display",
                    reply_markup=reply_mark,
                )
                
            
                selected = context.user_data['skill_set']
                await context.bot.send_message(chat_id=context._user_id, text=f"""your selected data is {selected}""")
                return STATE6          
async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return ConversationHandler.END


conversation = ConversationHandler(
    entry_points=[CommandHandler("resume", start_conversation)],
    states={
        STATE1: [CallbackQueryHandler(button)],
        STATE2: [CallbackQueryHandler(choosing_the_from_button)],
        STATE3: [CallbackQueryHandler(choose_experiance)],
        STATE4: [CallbackQueryHandler(choose_education)],
        STATE5: [CallbackQueryHandler(choose_project)],
        STATE6: [CallbackQueryHandler(choose_skill)],
    },

    fallbacks=[CommandHandler("stop", stop)],
)
