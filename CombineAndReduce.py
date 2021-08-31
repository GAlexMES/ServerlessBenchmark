import os
import csv

def main():
    directory = "/home/abrenn/dev/Uni/masterthesis/results/awsec2/write/210816_1507/jmeter/"
    with open(directory+"result.csv", "w") as result:
        wtr = csv.writer(result)
        wtr.writerow( ("threads", "request", "latency", "number of instances" ) )
        requestCounter = 0
        instanceCounter = 0
        for filename in os.listdir(directory):
            if filename == "result.csv":
                continue
            threads = filename.split(".")[0].split("-")[-1]
            with open(directory+filename, "r") as source:
                rdr = csv.reader(source)
                counter = 0
                firstLine = True
                for r in rdr:
                    if firstLine:
                        firstLine = False
                        continue

                    counter = counter + 1
                    requestNumber = int(r[2].split(" ")[2]) + requestCounter
                    latency = int(r[1]) - int(r[16])
                    newInstance = r[3] == "202"
                    instanceCounter = instanceCounter + 1 if newInstance else instanceCounter
                    wtr.writerow( (threads, requestNumber, latency, instanceCounter ) )
                requestCounter = requestCounter + counter

if __name__ == "__main__":
    # calling the main function
    main()
