# Alan the Alarm ⏰

![Descrição da imagem](https://drive.google.com/uc?export=view&id=1tBPMNA9rmN9P8VIXUJBgrUB9F3iAvP0l)

**Alan the Alarm** is a Discord bot that allows you to create alarms, manage time zones, and use useful commands in Discord text channels.

## Features

- Countdown alarm creation
- Set alarms for specific times
- Support for time zones (GMT)
- Commands to manage users and alarms
- View active alarms
- Message administration commands

## Installation

1. Clone this repository:
    ```bash
    git clone https://github.com/your-username/ata-alarm-bot.git
    ```

2. Install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. `bash` : Set your `Discord TOKEN` and your `MongoDB token` environment variable with your bot token:
    ```bash
    export ATA_TOKEN="your-token-here"
    export MONGODB_URI="your-token-here"
    ```
    `zshrc` :
	```
	echo "export ATA_TOKEN="your-token-here" >> ~/.zshrc
	echo "export MONGODB_URI=your-token-here" >> ~/.zshrc
 	source ~/.zshrc
	```

5. Run the bot `bash` :
    ```bash
    python bot.py
    ```
    `zshrc` :
   ```
   ./run.sh
   ```

## Commands

### Tutorial
- `alarm tutorial` : Displays an interactive tutorial with information about the bot's usage.

### User

- `alarm register (gmt)` : Registers the user with a specified time zone. Example: `alarm register GMT-3`
- `alarm delete_user` : Deletes the user.
- `alarm change_gmt (gmt)` : Changes the user's time zone. Example: `alarm change_gmt GMT-2`
- `alarm now` : Displays the current time in 24-hour format.
- `alarm nowus` : Displays the current time in 12-hour format (AM/PM).

### Alarms

- `alarm to HH:MM:SS ; message` : Sets an alarm for a specific amount of time from now.
  - Example : `alarm to 01:30:00 ; 1 hour and 30 minutes reminder`
- `alarm set HH:MM:SS ; message` : Sets an alarm for a specific time in 24-hour format.
  - Example : `alarm set 14:30:00 ; meeting reminder`
- `alarm setus HH:MM:SS AM/PM ; message` : Sets an alarm for a specific time in 12-hour format.
  - Example : `alarm setus 02:30:00 PM ; meeting reminder`
- `alarm active` : Displays all active alarms for the user.

### Message Administration

- `alarm count_messages` : Counts the total number of messages in the current channel.
- `alarm clear_messages (number)` : Deletes a specified number of messages in the current channel (admin privileges required).

## Security

- All data is handled with care and security, being stored in an encrypted format in the database.

## License

This project is licensed under the [MIT License](LICENSE).

## Contribution

Contributions are welcome! Please feel free to open issues or pull requests.

---

Developed by [Felipe Palermo](https://github.com/FelipPalermo)
