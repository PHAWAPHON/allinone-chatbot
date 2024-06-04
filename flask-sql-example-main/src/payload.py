import pytz
import datetime as dt

def format_data(events):
    result = []
    tz = pytz.timezone('Asia/Bangkok')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        if 'dateTime' in event['start']:
            start = dt.datetime.fromisoformat(start).astimezone(tz)
            date = start.date().isoformat()
            time = start.time().isoformat(timespec='minutes')
        else:
            date = start
            time = 'All Day'
        res = {
            'date': date,
            'time': time,
            'summary': event.get('summary', 'No Title'),
            'location': event.get('location', 'No Location'),
            'description': event.get('description', 'No Description'),
            'htmlLink': event.get('htmlLink', 'https://calendar.google.com')
        }
        result.append(res)
    return result

def format_room_flex(data):
    bubble_list = []
    for item in data:
        html_link = item.get('htmlLink', 'https://calendar.google.com')

        bubble = {
            "type": "bubble",
            "hero": {
                "type": "image",
                "url": "https://png.pngtree.com/png-clipart/20191027/ourlarge/pngtree-timer-icon-or-management-time-png-image_1842632.jpg",
                "size": "full",
                "aspectRatio": "20:13",
                "aspectMode": "cover"
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": item['summary'],
                        "weight": "bold",
                        "size": "xl",
                        "wrap": True
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "margin": "lg",
                        "spacing": "sm",
                        "contents": [
                            {
                                "type": "box",
                                "layout": "baseline",
                                "spacing": "sm",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "Date:",
                                        "color": "#aaaaaa",
                                        "size": "sm",
                                        "flex": 1
                                    },
                                    {
                                        "type": "text",
                                        "text": item['date'],
                                        "wrap": True,
                                        "color": "#666666",
                                        "size": "sm",
                                        "flex": 5
                                    }
                                ]
                            },
                            {
                                "type": "box",
                                "layout": "baseline",
                                "spacing": "sm",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "Time:",
                                        "color": "#aaaaaa",
                                        "size": "sm",
                                        "flex": 1
                                    },
                                    {
                                        "type": "text",
                                        "text": item['time'],
                                        "wrap": True,
                                        "color": "#666666",
                                        "size": "sm",
                                        "flex": 5
                                    }
                                ]
                            },
                            {
                                "type": "box",
                                "layout": "baseline",
                                "spacing": "sm",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "Location:",
                                        "color": "#aaaaaa",
                                        "size": "sm",
                                        "flex": 1
                                    },
                                    {
                                        "type": "text",
                                        "text": item['location'],
                                        "wrap": True,
                                        "color": "#666666",
                                        "size": "sm",
                                        "flex": 5
                                    }
                                ]
                            },
                            {
                                "type": "box",
                                "layout": "baseline",
                                "spacing": "sm",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "Description:",
                                        "color": "#aaaaaa",
                                        "size": "sm",
                                        "flex": 1
                                    },
                                    {
                                        "type": "text",
                                        "text": item['description'],
                                        "wrap": True,
                                        "color": "#666666",
                                        "size": "sm",
                                        "flex": 5
                                    }
                                ]
                            }
                        ]
                    }
                ]
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "spacing": "sm",
                "contents": [
                    {
                        "type": "button",
                        "style": "primary",
                        "height": "sm",
                        "action": {
                            "type": "uri",
                            "label": "More Info",
                            "uri": html_link
                        }
                    }
                ],
                "flex": 0
            }
        }
        bubble_list.append(bubble)
    carousel = {
        "type": "carousel",
        "contents": bubble_list
    }
    return carousel

def botnoipayload(flexdata):
    out = {
        "response_type": "object",
        "line_payload": [{
            "type": "flex",
            "altText": "Upcoming Events",
            "contents": flexdata
        }]
    }
    return out

def create_form_success_message(form_link):
    bubble = {
        "type": "bubble",
        "hero": {
            "type": "image",
            "url": "https://example.com/your-image-url.jpg",
            "size": "full",
            "aspectRatio": "20:13",
            "aspectMode": "cover"
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": "สร้าง form สำเร็จ!",
                    "weight": "bold",
                    "size": "xl"
                },
                {
                    "type": "text",
                    "text": "คุณสามารถเข้าถึงฟอร์มได้ที่:",
                    "margin": "md"
                },
                {
                    "type": "text",
                    "text": form_link,
                    "margin": "md",
                    "size": "sm",
                    "color": "#0000ff",
                    "action": {
                        "type": "uri",
                        "label": "Form Link",
                        "uri": form_link
                    }
                }
            ]
        }
    }
    return {
        "type": "flex",
        "altText": "Form Created",
        "contents": bubble
    }
