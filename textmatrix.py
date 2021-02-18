from common import SUNNY, CLOUDY, RAINY, SNOWY

"""
    MATRIX = " MINUSACHTNOLL" + \
             "EINZWOIVIERDRÜ" + \
             "ZWÖLFNÜN FÖFÜF" + \
             "ESEBENSÄCHSEIS" + \
             "DRISGIVIERTELF" + \
             "ZWÄNZGZÄHKOMMA" + \
             "VORAB ESCHALBI" + \
             "ELFI RACHTIDRÜ" + \
             " KEISÄCHSINÜNI" + \
             "SEBNIG NZÄHNI " + \
             "FÜFISEBEZWÖLFI" + \
             "ZWOI VIERIGRAD"
"""


class CharacterMatrix:
    MATRIX = "BMINUSACHTNOLL" + \
             "EINZWOIVIERDRÜ" + \
             "ZWÖLFNÜNRFÖFÜF" + \
             "ESEBENSÄCHSEIS" + \
             "DRISGIVIERTELF" + \
             "ZWÄNZGZÄHKOMMA" + \
             "VORABUESCHALBI" + \
             "ELFINRACHTIDRÜ" + \
             "OKEISÄCHSINÜNI" + \
             "SEBNIGMNZÄHNIU" + \
             "FÜFISEBEZWÖLFI" + \
             "ZWOIEVIERIGRAD"
    ROW_LEN = 14
    
    @classmethod
    def findTexts(cls, texts_array):
        result_coordinates = []
        pos_in_matrix = 0
        for text in texts_array:
            found_in_one_row = False
            while not found_in_one_row:
                found_start = cls.MATRIX.find(text.upper(), pos_in_matrix)
                print("found", text, "at", found_start)
                if found_start < 0:
                    return []
                found_end = found_start + len(text)            
                if found_start % cls.ROW_LEN + len(text) <= cls.ROW_LEN: # result is on one line
                    result_coordinates.extend([(p // cls.ROW_LEN, p % cls.ROW_LEN) for p in range(found_start, found_end)])
                    found_in_one_row = True
                pos_in_matrix = found_end
        return result_coordinates
    

class TextFinder:
    PIXEL_NUMBERS=[[[0,1], [0,2], [1,0], [1,3], [2,0], [2,3], [3,0], [3,3], [4,0], [4,3], [5,1], [5,2]],
                   [[3,0], [2,1], [1,2], [0,3], [1,3], [2,3], [3,3], [4,3], [5,3]],
                   [[1,0], [0,1], [0,2], [1,3], [2,3], [3,2], [4,1], [5,0], [5,1], [5,2], [5,3]],
                   [[0,0], [0,1], [0,2], [1,3], [2,1], [2,2], [3,3], [4,3], [5,0], [5,1], [5,2]],
                   [[2,0], [1,1], [0,2], [1,2], [2,2], [3,0], [3,1], [3,2], [3,3], [4,2], [5,2]],
                   [[0,0], [0,1], [0,2], [0,3], [1,0], [2,0], [2,1], [2,2], [3,3], [4,3], [5,0], [5,1], [5,2]],
                   [[0,1], [0,2], [0,3], [1,0], [2,0], [3,0], [4,0], [2,1], [2,2], [3,3], [4,3], [5,1], [5,2]],
                   [[0,0], [0,1], [0,2], [0,3], [1,3], [2,2], [3,2], [4,2], [5,2]],
                   [[0,1], [0,2], [1,0], [1,3], [2,1], [2,2], [3,0], [3,3], [4,0], [4,3], [5,1], [5,2]],
                   [[0,1], [0,2], [1,0], [1,3], [2,0], [2,3], [3,1], [3,2], [3,3], [4,3], [5,0], [5,1], [5,2]]]
    
    WEATHER = {SUNNY: [[0,5], [1,5], [2,5], [3,5], [4,5], [5,5]], 
               CLOUDY: [[5,1], [6,1], [7,1], [8,1], [9,1]], 
               RAINY: [[7,5], [8,5], [9,5], [10,5]], 
               SNOWY: [[6,7], [7,7], [8,7], [9,7], [10,7], [11,7]]}

    PERCENT = [[4,10], [4,13], [5,12], [6,11], [7,10], [7,13]]

    MINUTES_TEXTS = [["ES", "ESCH"], ["EIS", "AB"], ["ZWOI", "AB"], ["DRÜ", "AB"], ["VIER", "AB"], ["FÜF", "AB"], ["SÄCHS", "AB"], ["SEBE", "AB"], ["ACHT", "AB"], ["NÜN", "AB"], 
                     ["ZÄH", "AB"], ["ELF", "AB"], ["ZWÖLF", "AB"], ["DRI", "ZÄH", "AB"], ["VIER", "ZÄH", "AB"], ["VIERTEL", "AB"], ["SÄCH", "ZÄH", "AB"], ["SEB", "ZÄH", "AB"], ["ACHT", "ZÄH", "AB"], ["NÜN", "ZÄH", "AB"], 
                     ["ZWÄNZG", "AB"], ["EIN", "E", "ZWÄNZG", "AB"], ["ZWOI", "E", "ZWÄNZG", "AB"], ["DRÜ", "E", "ZWÄNZG", "AB"], ["VIER", "E", "ZWÄNZG", "AB"], ["FÜF", "VOR", "HALBI"], ["SÄCHS", "E", "ZWÄNZG", "AB"], ["SEBEN", "E", "ZWÄNZG", "AB"], ["ACHT", "E", "ZWÄNZG", "AB"], ["NÜN", "E", "ZWÄNZG", "AB"],
                     ["HALBI"], ["EIS", "AB", "HALBI"], ["ZWOI", "AB", "HALBI"], ["DRÜ", "AB", "HALBI"], ["VIER", "AB", "HALBI"], ["FÜF", "AB", "HALBI"], ["VIER", "E", "ZWÄNZG", "VOR"], ["DRÜ", "E", "ZWÄNZG", "VOR"], ["ZWOI", "E", "ZWÄNZG", "VOR"], ["EIN", "E", "ZWÄNZG", "VOR"], ["ZWÄNZG", "VOR"],
                     ["NÜN", "ZÄH", "VOR"], ["ACHT", "ZÄH", "VOR"], ["SEB", "ZÄH", "VOR"], ["SÄCH", "ZÄH", "VOR"], ["VIERTEL", "VOR"], ["VIER", "ZÄH", "VOR"], ["DRI", "ZÄH", "VOR"], ["ZWÖLF", "VOR"], ["ELF", "VOR"], ["ZÄH", "VOR"],
                     ["NÜN", "VOR"], ["ACHT", "VOR"], ["SEBE", "VOR"], ["SÄCHS", "VOR"], ["FÜF", "VOR"], ["VIER", "VOR"], ["DRÜ", "VOR"], ["ZWOI", "VOR"], ["EIS", "VOR"]]

    HOURS_TEXTS = ["ZWÖLFI", "EIS", "ZWOI", "DRÜ", "VIERI", "FÜFI", "SÄCHSI", "SEBNI", "ACHTI", "NÜNI", "ZÄHNI", "ELFI"]

    TEMP_BEFORE_DIGIT = [["NOLL"], ["EIS"], ["ZWOI"], ["DRÜ"], ["VIER"], ["FÜF"], ["SÄCHS"], ["SEBE"], ["ACHT"], ["NÜN"],  
                         ["ZÄH"], ["ELF"], ["ZWÖLF"], ["DRI", "ZÄH"], ["VIER", "ZÄH"], ["FÖF", "ZÄH"], ["SÄCH", "ZÄH"], ["SEBE", "ZÄH"], ["ACHT", "ZÄH"], ["NÜN", "ZÄH"],
                         ["ZWÄNZG"], ["EIN", "E", "ZWÄNZG"], ["ZWOI", "E", "ZWÄNZG"], ["DRÜ", "E", "ZWÄNZG"], ["VIER", "E", "ZWÄNZG"], ["FÜF", "E", "ZWÄNZG"], ["SÄCHS", "E", "ZWÄNZG"], ["SEBEN", "E", "ZWÄNZG"], ["ACHT", "E", "ZWÄNZG"], ["NÜN", "E", "ZWÄNZG"],
                         ["DRISG"], ["EIN", "E", "DRISG"], ["ZWOI", "E", "DRISG"], ["DRÜ", "E", "DRISG"], ["VIER", "E", "DRISG"], ["FÜF", "E", "DRISG"], ["SÄCHS", "E", "DRISG"], ["SEBEN", "E", "DRISG"], ["ACHT", "E", "DRISG"], ["NÜN", "E", "DRISG"]]

    TEMP_AFTER_DIGIT = [[], ["EIS"], ["ZWOI"], ["DRÜ"], ["VIER"], ["FÜF"], ["SÄCHS"], ["SEBE"], ["ACHT"], ["NÜN"]]

    MINUS = "MINUS"
    DOT = "KOMMA"
    DEGREE = "GRAD"
    
    def __init__(self):
        self._matrix = CharacterMatrix

    #@classmethod
    def _get_minutes_text(self, minutes):
        #try:
        return self.MINUTES_TEXTS[minutes]
        #except IndexError:
        #    print(f"Illegal Minute Value: {minutes}")
        #    return []
        
    #@classmethod
    def _get_hours_text(self, hours):
        return [self.HOURS_TEXTS[hours % 12]]  # zero == twelve, 13..24 == 1..12

    def get_time_positions(self, hours, minutes):
        print("Searching", hours, ":", minutes)
        if minutes == 25 or minutes >= 30:  # We say "Halbi <Next Hour>"
            hours = hours + 1
        return self._matrix.findTexts(self._get_minutes_text(minutes) + self._get_hours_text(hours))

    def get_temperature_positions(self, temperature):
        print("Searching Temp.", temperature)
        sign = [self.MINUS] if temperature < 0 else []
        before = int(round(abs(temperature), 0))
        after = int(round(abs(temperature) * 10, 0)) % 10
        after_texts = [self.DOT] + self.TEMP_AFTER_DIGIT[after] if after != 0 else []
        return self._matrix.findTexts(sign + self.TEMP_BEFORE_DIGIT[before] + after_texts + [self.DEGREE])

    def get_humidity_positions(self, humidity):
        print("Searching Hum.", humidity)
        humidity_int = int(round(humidity,0))
        ten_positions = self.PIXEL_NUMBERS[humidity_int // 10]
        one_positions = self.PIXEL_NUMBERS[humidity_int % 10]
        return [[p[0]+3, p[1]] for p in ten_positions] + [[p[0]+3, p[1]+5] for p in one_positions] + self.PERCENT

    def get_date_positions(self, day, month):
        print("Searching date", day, month)
        positions = [[p[0], p[1]+8] for p in self.PIXEL_NUMBERS[day % 10]]
        if day >= 10:
            positions += [[p[0], p[1]+3] for p in self.PIXEL_NUMBERS[day // 10]]
        positions += [[p[0]+6, p[1]+8] for p in self.PIXEL_NUMBERS[month % 10]]
        if month >= 10:
            positions += [[p[0]+6, p[1]+3] for p in self.PIXEL_NUMBERS[month // 10]]
        return positions + [[5, 13], [11, 13]]

    def get_weather_positions(self, weather_code):
        return self.WEATHER[weather_code]
 

if __name__ == "__main__":
    import time
    def debugPrintPositions(positions):
        out = ["              ",
            "              ",
            "              ",
            "              ",
            "              ",
            "              ",
            "              ",
            "              ",
            "              ",
            "              ",
            "              ",
            "              "]
        for r, c in positions:
            out[r] = out[r][:c] + CharacterMatrix.MATRIX[r*CharacterMatrix.ROW_LEN + c] + out[r][c+1:]
        print("-------------")
        print("\n".join(out))
    start = time.time()
    finder = TextFinder()
    for h in range(13):
        for m in range(60):
            positions = finder.get_time_positions(h, m)
            # debugPrintPositions(positions)

    print(time.time() - start)