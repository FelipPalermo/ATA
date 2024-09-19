# Alan the Alarm ⏰

![Descrição da imagem](https://drive.google.com/uc?export=view&id=1tBPMNA9rmN9P8VIXUJBgrUB9F3iAvP0l)
Alan the Alarm is a Discord bot designed to help you set alarms and reminders directly in your Discord server. With various commands, Alan can be used as a countdown timer, set alarms for specific times, and even display active alarms.

## Features ✨

- Set alarms for specific times or countdowns ⏳
- Choose between 24-hour format or 12-hour AM/PM format 🕑
- Receive alarm notifications via private messages 🔔
- Manage and view active alarms with ease 👁
- Admin tools to manage and clear chat messages 🧹
- Tutorial command to guide users on how to use the bot 📚

## Commands 📝

- **`alarm set HH:MM:SS ; message`**  
  Set an alarm for a specific time in 24-hour format. The optional `message` will be sent when the alarm goes off.  
  Example: `alarm set 15:45:00 ; Meeting with team`
  
- **`alarm setus HH:MM:SS AM/PM ; message`**  
  Set an alarm using the 12-hour AM/PM format.  
  Example: `alarm setus 02:30:00 PM ; Lunch break`
  
- **`alarm to HH:MM:SS ; message`**  
  Set a countdown timer that will go off after the specified time.  
  Example: `alarm to 00:30:00 ; Break time over`

- **`alarm active`**  
  View all your active alarms.

- **`alarm count_messages`**  
  Count the total number of messages in the current channel.

- **`alarm clear_messages <number>`**  
  Admin-only command to clear a specific number of messages from the channel.

- **`alarm tutorial`**  
  Displays an interactive tutorial to help you understand how to use Alan the Alarm.

## How to Install 🛠

1. Clone this repository :
   ```bash
   git clone https://github.com/yourusername/alan-the-alarm.git


2. Install Dependencies :
   ```bash
   pip install -r requirements.txt
  
3. Set up your environment variables in a .env file : 
  ```bash
   ATA_TOKEN=your_discord_bot_token
   MONGODB_URI=your_mongo_db_uri
  ```

4. Run the bot :
```bash 
  ./run.sh
```

Dependencies 📦

	•	discord.py: Python library for the Discord API
	•	pymongo: To store and manage alarms in MongoDB
	•	aiohttp: For asynchronous requests
	•	datetime: To handle time-based functionalities
	•	re: For regex-based parsing of time inputs
	•	certifi: For SSL context in secure connections

License 📄

This project is licensed under the MIT License - see the LICENSE file for details.

Contributions 🤝

Feel free to submit pull requests, report bugs, or suggest features via GitHub Issues. Contributions are welcome!


