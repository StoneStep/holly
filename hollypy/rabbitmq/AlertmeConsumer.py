# coding=utf-8
import json, smtplib
import pika

def send_mail(recipients,subject,message):
    """E-mail generator for receive alerts"""
    headers = ("From %s,\r\nTo: \r\nDate:\r\n"+
               "Subject: %s\r\n\r\n")%("1225834905@qq.com",subject)
    smtp_server = smtplib.SMTP()
    smtp_server.connect("",25)
    smtp_server.sendmail("",recipients,headers+str(message))
    smtp_server.close()

def critical_notify(channel,method,header,body):
    EMAIL_RECIPS = ["",]
    message = json.loads(body)
    # send_mail(EMAIL_RECIPS,"CRITICAL ALERT",message)
    print("send critical_notify alert via email"+str(message))
    channel.basic_ack(delivery_tag=method.delivery_tag)

def rate_limit_notify(channel,method,header,body):
    EMAIL_RECIPS = ["",]
    message = json.load(body)
    # send_mail(EMAIL_RECIPS,"RATE LIMIT ALERT!",message)
    print("send rate_limit_notify alert via email"+str(message))
    channel.basic_ack(delivery_tag=method.delivery_tag)

if __name__ == "__main__":
    AMQP_SERVER = "localhost"
    AMQP_USER = "alert_user"
    AMQP_PASS = "alertme"
    AMQP_VHOST = "/"
    AMQP_EXCHANGE = "alerts"
    creds_broker = pika.PlainCredentials(AMQP_USER,AMQP_PASS)
    conn_params = pika.ConnectionParameters(AMQP_SERVER,virtual_host=AMQP_VHOST,
                                            credentials = creds_broker)
    conn_broker = pika.BlockingConnection(conn_params)

    channel = conn_broker.channel()
    channel.exchange_declare(exchange=AMQP_EXCHANGE,type="topic",auto_delete=False)

    channel.queue_declare(queue="critical",auto_delete=False)
    channel.queue_bind(queue="critical",exchange=AMQP_EXCHANGE,routing_key="critical.*")
    channel.queue_declare(queue="rate_limit",auto_delete=False)
    channel.queue_bind(queue="rate_limit",exchange=AMQP_EXCHANGE,routing_key="*.rate_limit")
    channel.basic_consume(critical_notify,queue="critical",no_ack=False,consumer_tag="critical")
    channel.basic_consume(rate_limit_notify,queue="rate_limit",no_ack=False,consumer_tag="rate_limit")
    channel.start_consuming()

