# Question-Telegram-Bot  
A Telegram bot built in Python using the official Telegram Bot API library (`python-telegram-bot`) for flexibly collecting public, anonymous questions and other feedback types, and responding to them. As of 11/03/2025, only a version with messages in Russian is available; I will add the English language version in a week.

## How It Works  
The bot responds to the `/start` command with an initial message. Afterward, it receives the user’s question and forwards the details to a Telegram group specified in the code (`GROUP_CHAT_ID`). Administrators (the code example includes two, though this number can be adjusted) can message users who have previously contacted the bot and modify the initial message using the `/send` and `/reset` commands.

## Receiving Questions  
Users are presented with three question types via buttons. The design intention is for anonymous and public questions to be directed to the club’s speaker, while organizational questions are meant for club staff:  
1. **Anonymous**: The bot prompts for the question without collecting names or usernames. Administrators only see the question, ensuring user anonymity as a fundamental right.  
2. **Public**: The bot requests the user’s name and question in two separate messages. The provided name, username, and question are shared in the group.  
3. **Organizational**: The bot collects the user’s question about club operations. The username and question are recorded for staff to address later in the chat.  

## Admin Commands  
Two commands are available to admins:  
1. **`/send <user_id> message`**:  
   - The bot verifies admin eligibility. Unauthorized attempts trigger a notification to other admins.  
   - If valid, the message is sent to the specified user. Invalid inputs display a warning in the chat with an explanation.  
   - *Message* can span multiple words; quotation marks are optional.  

2. **`/reset new message`**:  
   - The bot checks admin eligibility again, notifying others if unauthorized.  
   - If valid, the initial message (shown after `/start`) updates to *new message*. Invalid inputs retain the current message and show an error.  
   - **Note**: The initial message is hardcoded. Restarting the script reverts it to the original version.  

## Cancel Command
All users can use the `/cancel` command to exit the current question selection process.

## Requirements and Hosting
The only requirement for the script is the `python-telegram-bot` library, compatible with v21.10 To host, run `python3 telegram_bot.py`.

For further inquiries or suggestions, reach out to msmirnov@nes.ru.
