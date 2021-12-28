import RpcClient

client = RpcClient.RpcClient()
client.connect('127.0.0.1', 5000)
# sum = client.sum(1.18, 2.2)
# print(f'sum: {sum}')
str = client.upper('school')
print(f'str: {str}')