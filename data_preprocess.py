

def get_all_info(hotel):
    all_text = ''
    for k, v in hotel.items():
        all_text += str(k) + ':' + str(v) + '\n'
    return all_text