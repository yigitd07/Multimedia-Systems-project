import csv
from collections import Counter
import matplotlib.pyplot as plt

# CSV dosyasından sınıf sayılarını oku
def read_detections(file_path="detections.csv"):
    counter = Counter()
    with open(file_path, mode="r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cls = row["class"]
            count = int(row["count"])
            counter[cls] += count
    return counter

# Grafik çiz
def plot_detections(counter):
    labels = list(counter.keys())
    values = list(counter.values())

    plt.figure(figsize=(8, 5))
    bars = plt.bar(labels, values, color="skyblue")
    plt.title("Toplam Nesne Tespitleri")
    plt.xlabel("Sınıf (class)")
    plt.ylabel("Toplam Sayı")

    # Sayıları çubukların üstüne yaz
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2.0, yval + 0.5, int(yval), ha='center')

    plt.tight_layout()
    plt.savefig("detections_plot.png")
    plt.show()

if __name__ == "__main__":
    counts = read_detections()
    plot_detections(counts)

