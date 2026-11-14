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
                # print("found", text, "at", found_start)
                if found_start < 0:
                    return []
                found_end = found_start + len(text)            
                if found_start % cls.ROW_LEN + len(text) <= cls.ROW_LEN: # result is on one line
                    for p in range(found_start, found_end):
                        result_coordinates.append((p // cls.ROW_LEN, p % cls.ROW_LEN))
                    found_in_one_row = True
                pos_in_matrix = found_end
        return result_coordinates
    

class TextFinder:
    # One byte per coordinate: row * 14 + column. Keep fixed patterns in
    # immutable bytes instead of hundreds of tiny Python coordinate lists.
    PIXEL_NUMBERS = (
        b'\x00\x01\x02\x03\x0e\x11\x1c\x1f*-8;FGHI',
        b'\x03\x11\x1f-;I',
        b'\x00\x01\x02\x03\x11\x1f\x1e\x1d\x1c*8FGHI',
        b'\x00\x01\x02\x03\x11\x1c\x1d\x1e\x1f-;FGHI',
        b'\x00\x03\x0e\x11\x1c\x1d\x1e\x1f-;I',
        b'\x00\x01\x02\x03\x0e\x1c\x1d\x1e\x1f-;FGHI',
        b'\x00\x01\x02\x03\x0e\x1c\x1d\x1e\x1f*8-;FGHI',
        b'\x00\x01\x02\x03\x11\x1f-;I',
        b'\x00\x01\x02\x03\x0e\x11\x1c\x1d\x1e\x1f*8-;FGHI',
        b'\x00\x01\x02\x03\x0e\x11\x1c\x1d\x1e\x1f-;FGHI',
    )

    WEATHER = {SUNNY: b'\x05\x13!/=K',
               CLOUDY: b'GUcq\x7f',
               RAINY: b'gu\x83\x91',
               SNOWY: b'[iw\x85\x93\xa1'}

    PERCENT = b'BER_lo'
    LUM = b'\x81\x8f\x9d\x91\x9f\xa0\x93\xa1\x95\xa3\x96\x97\xa5\x98\x99\xa7'
    
    MINUTES_TEXTS = [["ES", "ESCH"], ["EIS", "AB"], ["ZWOI", "AB"], ["DRÜ", "AB"], ["VIER", "AB"], ["FÜF", "AB"], ["SÄCHS", "AB"], ["SEBE", "AB"], ["ACHT", "AB"], ["NÜN", "AB"], 
                     ["ZÄH", "AB"], ["ELF", "AB"], ["ZWÖLF", "AB"], ["DRI", "ZÄH", "AB"], ["VIER", "ZÄH", "AB"], ["VIERTEL", "AB"], ["SÄCH", "ZÄH", "AB"], ["SEB", "ZÄH", "AB"], ["ACHT", "ZÄH", "AB"], ["NÜN", "ZÄH", "AB"], 
                     ["ZWÄNZG", "AB"], ["EIN", "E", "ZWÄNZG", "AB"], ["ZWOI", "E", "ZWÄNZG", "AB"], ["DRÜ", "E", "ZWÄNZG", "AB"], ["VIER", "E", "ZWÄNZG", "AB"], ["FÜF", "VOR", "HALBI"], ["VIER", "VOR", "HALBI"], ["DRÜ", "VOR", "HALBI"], ["ZWOI", "VOR", "HALBI"], ["EIS", "VOR", "HALBI"],
                     ["HALBI"], ["EIS", "AB", "HALBI"], ["ZWOI", "AB", "HALBI"], ["DRÜ", "AB", "HALBI"], ["VIER", "AB", "HALBI"], ["FÜF", "AB", "HALBI"], ["SÄCHS", "AB", "HALBI"], ["SEBE", "AB", "HALBI"], ["ACHT", "AB", "HALBI"], ["NÜN", "AB", "HALBI"], ["ZWÄNZG", "VOR"],
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
        if minutes >= 25:  # We say "Halbi <Next Hour>" and "zäh vor <Next Hour>"
            hours = hours + 1
        return self._matrix.findTexts(self._get_minutes_text(minutes) + self._get_hours_text(hours))

    def get_temperature_positions(self, temperature):
        print("Searching Temp.", temperature)
        sign = [self.MINUS] if temperature < 0 else []
        before = int(abs(temperature))
        after = int(round(abs(temperature) * 10, 0)) % 10
        after_texts = [self.DOT] + self.TEMP_AFTER_DIGIT[after] if after != 0 else []
        return self._matrix.findTexts(sign + self.TEMP_BEFORE_DIGIT[before] + after_texts + [self.DEGREE])

    @staticmethod
    def _append_positions(positions, packed, row_offset=0, column_offset=0):
        # Keep the public list-of-coordinates interface, but build only one
        # result list instead of concatenating multiple intermediate lists.
        for pixel in packed:
            positions.append([pixel // 14 + row_offset, pixel % 14 + column_offset])

    def get_humidity_positions(self, humidity):
        print("Searching Hum.", humidity)
        humidity_int = int(round(humidity,0))
        positions = []
        self._append_positions(positions, self.PIXEL_NUMBERS[humidity_int // 10], 3)
        self._append_positions(positions, self.PIXEL_NUMBERS[humidity_int % 10], 3, 5)
        self._append_positions(positions, self.PERCENT)
        return positions

    def get_date_positions(self, day, month):
        print("Searching date", day, month)
        positions = []
        self._append_positions(positions, self.PIXEL_NUMBERS[day % 10], 0, 8)
        if day >= 10:
            self._append_positions(positions, self.PIXEL_NUMBERS[day // 10], 0, 3)
        self._append_positions(positions, self.PIXEL_NUMBERS[month % 10], 6, 8)
        if month >= 10:
            self._append_positions(positions, self.PIXEL_NUMBERS[month // 10], 6, 3)
        positions.append([5, 13])
        positions.append([11, 13])
        return positions

    def get_luminance_position(self, luminance):
        print("Searching Lum.", luminance)
        luminance_int = min(int(round(luminance,0)), 999)
        positions = []
        if luminance_int >= 100:
            self._append_positions(positions, self.PIXEL_NUMBERS[luminance_int // 100], 2)
        if luminance_int >= 10:
            self._append_positions(positions, self.PIXEL_NUMBERS[(luminance_int // 10) % 10], 2, 5)
        self._append_positions(positions, self.PIXEL_NUMBERS[luminance_int % 10], 2, 10)
        self._append_positions(positions, self.LUM)
        return positions

    def get_weather_positions(self, weather_code):
        positions = []
        self._append_positions(positions, self.WEATHER[weather_code])
        return positions
 

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