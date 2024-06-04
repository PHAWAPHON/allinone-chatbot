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
            'htmlLink': event.get('htmlLink', 'https://calendar.google.com')  # เพิ่ม htmlLink
        }
        result.append(res)
    return result

def format_room_flex(data):
    bubble_list = []
    for item in data:
        # Ensure 'htmlLink' exists in the item, set a default value if it doesn't
        html_link = item.get('htmlLink', 'https://calendar.google.com')  # Default link

        bubble = {
            "type": "bubble",
            "hero": {
                "type": "image",
                "url": "https://insights.nconnect.asia/wp-content/uploads/2022/10/1_FKBM6mtZlboou8AHhGjqpQ.png",
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
                            "uri": html_link  # Use htmlLink from event data
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

def format_reminder_selection(day):
    bubble = {
        "type": "bubble",
        "header": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": f"ปฏิทินแจ้งเตือนล่วงหน้า {day} วัน",
                    "weight": "bold",
                    "size": "xl",
                    "align": "center"
                }
            ]
        },
        "hero": {
            "type": "image",
            "url": "",
            "size": "full",
            "aspectRatio": "1.51:1",
            "aspectMode": "fit"
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": f"คุณได้เลือกแจ้งเตือนล่วงหน้า {day} วัน",
                    "wrap": True,
                    "align": "center"
                }
            ]
        },
        "footer": {
            "type": "box",
            "layout": "horizontal",
            "spacing": "sm",
            "contents": [
                {
                    "type": "button",
                    "style": "primary",
                    "height": "sm",
                    "action": {
                        "type": "message",
                        "label": f"{day} วัน",
                        "text": f"แจ้งเตือนล่วงหน้า {day} วัน"
                    },
                    "color": "#4CAF50" if day == 1 else "#2196F3" if day == 2 else "#FF5722" if day == 3 else "#673AB7"  # Color based on day
                }
            ]
        }
    }
    return bubble

def create_reminder_selection_bubble():
    bubble = {
        "type": "bubble",
        "header": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": "ปฏิทินแจ้งเตือนล่วงหน้า",
                    "weight": "bold",
                    "size": "xl",
                    "align": "center"
                }
            ]
        },
        "hero": {
            "type": "image",
            "url": "https://cdn-icons-png.flaticon.com/512/4116/4116423.png",
            "size": "full",
            "aspectRatio": "1.51:1",
            "aspectMode": "fit"
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": "คุณสามารถเลือกวันแจ้งเตือนล่วงหน้าตามที่ต้องการได้เลย",
                    "wrap": True,
                    "align": "center"
                }
            ]
        },
        "footer": {
            "type": "box",
            "layout": "horizontal",
            "spacing": "sm",
            "contents": [
                {
                    "type": "button",
                    "style": "primary",
                    "height": "sm",
                    "action": {
                        "type": "message",
                        "label": "1 วัน",
                        "text": "แจ้งเตือนล่วงหน้า 1 วัน"
                    },
                    "color": "#4CAF50"  # Green
                },
                {
                    "type": "button",
                    "style": "primary",
                    "height": "sm",
                    "action": {
                        "type": "message",
                        "label": "2 วัน",
                        "text": "แจ้งเตือนล่วงหน้า 2 วัน"
                    },
                    "color": "#2196F3"  # Blue
                },
                {
                    "type": "button",
                    "style": "primary",
                    "height": "sm",
                    "action": {
                        "type": "message",
                        "label": "3 วัน",
                        "text": "แจ้งเตือนล่วงหน้า 3 วัน"
                    },
                    "color": "#FF5722"  # Deep Orange
                },
                {
                    "type": "button",
                    "style": "primary",
                    "height": "sm",
                    "action": {
                        "type": "message",
                        "label": "7 วัน",
                        "text": "แจ้งเตือนล่วงหน้า 7 วัน"
                    },
                    "color": "#673AB7"  # Deep Purple
                }
            ]
        }
    }
    return bubble
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
