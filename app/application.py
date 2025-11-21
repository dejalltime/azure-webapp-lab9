from flask import Flask, render_template, request
from azure.data.tables import TableServiceClient
from azure.servicebus import ServiceBusClient, ServiceBusMessage
from azure.identity import DefaultAzureCredential

app = Flask(__name__)

COSMOS_URL = "https://lab9cosmosaccount.table.core.windows.net"
TABLE_NAME = "MyTable"
SERVICEBUS_NAMESPACE = "lab9servicebus.servicebus.windows.net"
TOPIC_NAME = "MyTopic"

credential = DefaultAzureCredential()

table_service = TableServiceClient(endpoint=COSMOS_URL, credential=credential)
table_client = table_service.get_table_client(TABLE_NAME)

servicebus_client = ServiceBusClient(SERVICEBUS_NAMESPACE, credential=credential)

@app.route('/', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        try:
            entity = table_client.get_entity(partition_key="Username", row_key=username)
            if entity["Password"] == password:
                with servicebus_client.get_topic_sender(topic_name=TOPIC_NAME) as sender:
                    sender.send_messages(ServiceBusMessage(f"User {username} logged in"))
                return render_template("home.html")
        except:
            pass

        return render_template("index.html", error="Invalid credentials")

    return render_template("index.html")