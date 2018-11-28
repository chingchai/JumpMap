Refer_Map = [
['Google Map', 'https://www.google.com/maps/@@LAT@,@LON@,@Z@z/data=!3m1!1e3', 'https://www.google.com/maps/place/@LAT@,@LON@/@@LAT@,@LON@,@Z@z/data=!3m1!1e3']
]

def referJumpMap():
    '''ฟังก์ชั่นนี้จะใช้เพิ่มค่าข้อมูลที่ได้จากLat, Lon '''
    post =[]
    for x in Refer_Map:
        post.append(x[0])
    return post