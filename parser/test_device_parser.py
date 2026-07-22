from pdf_parser import PDFReader
from device_parcer import DeviceParser
from motion_parser import MotionParser
from position_parser import PositionParser
from timer_parser import TimerParser
from program_parser import ProgramParser
from statement_parser import StatementParser
from network_parser import NetworkParser
#from device_comment import parse_pdf
    
reader = PDFReader("docs/gxworks_exports")

docs = reader.read_all()
parser = DeviceParser()
motion_parser = MotionParser()
position_parser = PositionParser()
timer_parser = TimerParser()
program_parser = ProgramParser()
statement_parser = StatementParser()
network_parser = NetworkParser()
#comment_parser = parse_pdf()

for name, text in docs.items():

    if "device_comment" in name.lower() or "device_list" in name.lower():

        parser.parse(text)

    elif "motion" in name.lower():
        motion_parser.parse(text)

    elif "position" in name.lower() or "axis" in name.lower():
        position_parser.parse(text)

    elif "tc" in name.lower():
        timer_parser.parse(text)   

    elif "program" in name.lower(): 
        program_parser.parse(text)  

    elif "statement" in name.lower(): 
        statement_parser.parse(text)    

    elif "network" in name.lower(): 
        network_parser.parse(text)  


parser.save_json()
motion_parser.save()
position_parser.save()
timer_parser.save()
program_parser.save()
statement_parser.save()
network_parser.save()
#comment_parser.save()


print("\nAll parsing completed successfully!")


