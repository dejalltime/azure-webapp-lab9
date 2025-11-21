from flask import Flask, render_template, request
from azure.data.tables import TableServiceClient
from azure.servicebus import ServiceBusClient, ServiceBusMessage

app = Flask(__name__)

# ⚠️ Lab only – in real apps, move these to config / Key Vault.
TABLE_CONNECTION_STRING = "DefaultEndpointsProtocol=https;AccountName=lab9cosmosaccount;AccountKey=azQuwfkICSxGgWcyBkeoZoUSWkafuebUFIHtLzCXOYdDpjcM31BqcAVLtx9TZPXCZEXXelr0MVauACDb8z7hww==;TableEndpoint=https://lab9cosmosaccount.table.cosmos.azure.com:443/;"
TABLE_NAME = "MyTable"

SERVICEBUS_CONNECTION_STRING = "Endpoint=sb://lab9servicebus.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=T8vqJGlm+UpnKApTofEEQxVxrXjEwoZIG+ASbJwuiaU="
TOPIC_NAME = "MyTopic"


def get_table_client():
    """Create a Table client for MyTable."""
    table_service = TableServiceClient.from_connection_string(TABLE_CONNECTION_STRING)
    return table_service.get_table_client(TABLE_NAME)


def get_servicebus_sender():
    """Create a Service Bus topic sender."""
    servicebus_client = ServiceBusClient.from_connection_string(SERVICEBUS_CONNECTION_STRING)
    return servicebus_client.get_topic_sender(topic_name=TOPIC_NAME)


@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        try:
            table_client = get_table_client()

            # Get entity: PartitionKey = "Username", RowKey = <username>
            entity = table_client.get_entity(
                partition_key="Username",
                row_key=username,
            )

            # Compare the password stored in table
            if entity.get("Password") == password:
                # Publish message to Service Bus Topic
                with get_servicebus_sender() as sender:
                    message = ServiceBusMessage(f"User {username} logged in successfully")
                    sender.send_messages(message)

                return render_template("home.html")

        except Exception as e:
            # This will show up in Log Stream / Kudu
            print("Error during login:", e)

        # Invalid login or error
        return render_template("index.html", msg="Invalid username or password.")

    # GET request – just show the login page
    return render_template("index.html", msg=None)
