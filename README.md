# 邮件自动回复程序

## 概览
这个 Python 程序能自动回复指定 Gmail 账户收到的新邮件。它会向每个发件人发送一封预设消息的新邮件，而不是回复。
处理后会删除收到的邮件，并将发件人邮箱记录到 CSV 文件中。
如果已经记录过该邮箱，则不会重复记录。
此外，该程序可以通过 Telegram 机器人向指定的 Telegram 聊天中发送程序在运行中出现的关键错误消息。

## 注意
由于gmail的限制，需要手动在邮箱设置过滤器，允许所有邮件都不是垃圾邮件。具体设置方法请自行搜索。

## 功能
- 自动对新邮件发送预设消息的回复。
- 处理后删除邮件。
- 不重复记录发件人的邮箱地址。
- 向 Telegram 聊天发送关键错误通知。
- 通过 `config.ini` 文件进行配置。
- 邮件正文支持回车，可以使用："\n"作为回车转译。

## 配置（`config.ini`）
要正确使用此程序，需要在 `config.ini` 文件中设置以下配置：

```ini
[settings]
email = yourgmail@gmail.com          # Gmail 地址
password = yourpassword              # Gmail 密码
smtp_server = smtp.gmail.com         # Gmail 的 SMTP 服务器
smtp_port = 587                      # Gmail 的 SMTP 端口
imap_server = imap.gmail.com         # Gmail 的 IMAP 服务器
imap_port = 993                      # Gmail 的 IMAP 端口
check_interval = 60                  # 检查新邮件的时间间隔（秒）
email_log_file = email_log.csv       # 记录邮箱地址的 CSV 文件路径
log_file = app_log.csv               # 通用日志文件路径
bot_token = your_telegram_bot_token  # Telegram 机器人的令牌
chat_id = your_telegram_chat_id      # 将消息发送至的 Telegram 聊天 ID

[message]
subject = 来自您的公司的自动回复  # 自动回复邮件的主题
body = 感谢您的邮件。我们将尽快与您联系。  # 自动回复邮件的内容
```

## 依赖项
该程序需要以下 Python 库：
- `imaplib`
- `smtplib`
- `email`
- `configparser`
- `os`
- `csv`
- `time`
- `logging`
- `requests`
- `datetime`

确保您的 Python 环境中安装了所有这些库。您可以使用 pip 安装它们：
```bash
pip3 install requests
```

## 运行程序
配置好配置文件并确保安装了所有依赖项后，执行 Python 脚本即可运行程序：
```bash
python3 autosendmail.py
```

确保 `config.ini` 文件配置正确，并且与脚本位于同一目录，或者在脚本中提供正确的路径。

## 日志记录
- **邮件日志**：在 `email_log.csv` 中记录邮件地址，确保每个发件人只被记录一次。
- **应用日志**：在 `app_log.csv` 中存储一般日志和错误消息，包括详细的错误描述和时间戳。
- **Telegram 通知**：在出现关键错误时，将通知发送到配置的 Telegram 聊天。
```
