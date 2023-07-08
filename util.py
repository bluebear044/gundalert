import smtplib
from log_util import logger
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def sendEmail(sender_email, sender_password, receiver_email, subject, message):
    msg = MIMEMultipart('alternative')
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = subject

    msg.attach(MIMEText(message, "html"))

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()

    server.login(sender_email, sender_password)

    server.send_message(msg)

    server.quit()


def compareDictsArray(dicts1, dicts2):

    diffDicts = []

    # 길이가 더 짧은 배열을 기준으로 순회
    for i in range(len(dicts1)):
        dict1 = dicts1[i]
        
        # 길이가 더 짧은 배열의 인덱스가 더 작은 범위 내에 있을 때만 비교
        if i < len(dicts2):
            dict2 = dicts2[i]
            
            # 딕셔너리 비교
            if dict1 != dict2:
                # diffDicts.append((dict1, dict2))
                diffDicts.append(dict2) # dicts2에 변화된 것만 append 하도록 바꿈
        else:
            # 길이가 다른 경우에는 차이가 있는 것으로 간주
            diffDicts.append(dict1)

    # 길이가 긴 배열에 남은 딕셔너리들도 차이가 있는 것으로 간주
    for j in range(len(dicts1), len(dicts2)):
        dict2 = dicts2[j]
        diffDicts.append(dict2)

    logger.info(diffDicts)

    return diffDicts


def sortDictsArray(arr, key):
    sortedArr = sorted(arr, key=lambda x: x[key])
    return sortedArr


def convertStringToNumber(param):
    try:
        number = int(param.replace(',', ''))
        return number
    except ValueError:
        print(f"Error: Unable to convert '{param}' to a number.")
        return None


if __name__ == "__main__":
    dicts1 = [{'name': 'Alice', 'age': 1}, {'name': 'Bob', 'age': 1}, {'name': 'Doba', 'age': 1}, {'name': 'Eyota', 'age': 1}]
    dicts2 = [{'name': 'Alice', 'age': 1}, {'name': 'Bob', 'age': 1}, {'name': 'Charlie', 'age': 1}, {'name': 'Eyota', 'age': 1}]

    sorted_dicts1 = sortDictsArray(dicts1, 'name')
    sorted_dicts2 = sortDictsArray(dicts2, 'name')
    diff = compareDictsArray(sorted_dicts1, sorted_dicts2)
