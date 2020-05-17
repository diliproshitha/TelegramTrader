# TelegramTrader

## Forex signals automator for Metatrader4 and Telegram.

Most of the forex signal providers use Telegram to distribute signals. Using this python program, order placing can be automated by using Metatrader 4. 

For porting MT4 with python, I used DarwinX ZMQ connector. Check [their repo](https://github.com/darwinex/DarwinexLabs/tree/master/tools/dwx_zeromq_connector/v2.0.1) to configure ZMQ for Metatrader 4.

Telethon library is used to create telegram listener server. You need to install it using pip or Conda.

resources/user.properties file contains MT4 server details, Symbols prefix (Some brokers add weired letters after currency Symbols like GBPJPY.u :| ), Lot Size, Excluded Pairs, and Pairs need to accept. Configure them as you need. I have added sample details to those properties. 
PricePointFactors also should be updated accoring to your broker.
