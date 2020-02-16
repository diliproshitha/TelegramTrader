from util.message_util import analyzeMessage
from message_operations.message_reader import getDecoratedMessage

message = "👨‍💻BUY GBPUSD 1.2960\n🔸SL 1.2910\n🔹TP 1.3060\nAll Copyright© Reserved."

order_dict = analyzeMessage(message)
print(getDecoratedMessage(order_dict))