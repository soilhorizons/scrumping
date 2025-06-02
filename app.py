from flask import Flask, request, jsonify, render_template_string
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime

app = Flask(__name__)

# Fix for postgres:// vs postgresql://
database_url = os.environ.get('DATABASE_URL')
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)
app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class Spot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lat = db.Column(db.Float, nullable=False)
    lon = db.Column(db.Float, nullable=False)
    type_of_fruit = db.Column(db.String(100), nullable=False)
    symbol = db.Column(db.String(50), nullable=False)
    scrumping_month = db.Column(db.Integer, nullable=False)
    your_name = db.Column(db.String(100), nullable=False)
    notes = db.Column(db.Text)
    date_added = db.Column(db.String(20), default=lambda: datetime.now().strftime('%Y-%m-%d'))

    def to_dict(self):
        return {
            "id": self.id,
            "lat": self.lat,
            "lon": self.lon,
            "type_of_fruit": self.type_of_fruit,
            "symbol": self.symbol,
            "scrumping_month": self.scrumping_month,
            "your_name": self.your_name,
            "notes": self.notes,
            "date_added": self.date_added
        }

class Spot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lat = db.Column(db.Float, nullable=False)
    lon = db.Column(db.Float, nullable=False)
    type_of_fruit = db.Column(db.String(100), nullable=False)
    symbol = db.Column(db.String(50), nullable=False)
    scrumping_month = db.Column(db.Integer, nullable=False)
    your_name = db.Column(db.String(100), nullable=False)
    notes = db.Column(db.Text)
    date_added = db.Column(db.String(20), default=lambda: datetime.now().strftime('%Y-%m-%d'))

# To create the tables (do this once, e.g. from a shell):
# >>> from app import db
# >>> db.create_all()

@app.route("/add_spot", methods=["POST"])
def add_spot():
    data = request.get_json()
    spot = Spot(
        lat=data["lat"],
        lon=data["lon"],
        type_of_fruit=data["type_of_fruit"],
        symbol=data["symbol"],
        scrumping_month=int(data["scrumping_month"]),
        your_name=data["your_name"],
        notes=data.get("notes", "")
    )
    db.session.add(spot)
    db.session.commit()
    return jsonify({"success": True})

spots = Spot.query.order_by(Spot.id).all()


SPOTS_FILE = "scrumping_spots.json"

SYMBOL_OPTIONS = [
    {"label": "Apple", "value": "apple", "icon": "https://cdn-icons-png.flaticon.com/512/415/415733.png"},
    {"label": "Pear", "value": "pear", "icon": "https://cdn-icons-png.flaticon.com/128/415/415716.png"},
    {"label": "Plum", "value": "plum", "icon": "https://cdn-icons-png.flaticon.com/128/4057/4057267.png"},
    {"label": "Cherry", "value": "cherry", "icon": "https://cdn-icons-png.flaticon.com/128/1791/1791306.png"},
    {"label": "Nut", "value": "nut", "icon": "https://cdn-icons-png.flaticon.com/128/7451/7451659.png"},
    {"label": "Persimmon", "value": "persimmon", "icon": "https://cdn-icons-png.flaticon.com/128/12404/12404784.png"},
    {"label": "Blackberry", "value": "blackberry", "icon": "https://cdn-icons-png.flaticon.com/128/4332/4332794.png"},
    {"label": "Mulberry", "value": "mulberry", "icon": "https://cdn-icons-png.flaticon.com/128/13449/13449659.png"},
    {"label": "Strawberry", "value": "strawberry", "icon": "https://cdn-icons-png.flaticon.com/128/9421/9421253.png"},
    {"label": "Raspberry", "value": "raspberry", "icon": "https://cdn-icons-png.flaticon.com/128/1542/1542487.png"},
    {"label": "Fig", "value": "fig", "icon": "https://cdn-icons-png.flaticon.com/128/6192/6192458.png"},
    {"label": "Flower", "value": "flower", "icon": "https://cdn-icons-png.flaticon.com/128/11504/11504574.png"},
    {"label": "Other", "value": "other", "icon": "https://cdn-icons-png.flaticon.com/128/5726/5726678.png"},
]

STAR_ICON = "https://cdn-icons-png.flaticon.com/512/1828/1828884.png"

def load_spots():
    if os.path.exists(SPOTS_FILE):
        with open(SPOTS_FILE, "r") as f:
            return json.load(f)
    return []

def save_spots(spots):
    with open(SPOTS_FILE, "w") as f:
        json.dump(spots, f)

@app.route("/")
def index():
    return "<h2>Go to <a href='/map'>/map</a> to see the map.</h2>"

@app.route("/map")
def map():
    spots = load_spots()
    start_lat, start_lon = (32.5007, -110.1246)
    if spots:
        last_spot = spots[-1]
        start_lat, start_lon = last_spot['lat'], last_spot['lon']
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Scrumping Map</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css"/>
        <style>
            #map { width: 100vw; height: 100vh; }
            #addSpotBtn {
                position: absolute;
                top: 10px;
                right: 10px;  /* Moved to right */
                z-index: 1001;
            }
            #saveSpotBtn {
                display: none;
                position: absolute;
                top: 50px;
                right: 10px;  /* Moved to right */
                z-index: 1002;
            }
            #spotModal {
                display: none;
                position: fixed;
                z-index: 2000;
                left: 0; top: 0; width: 100vw; height: 100vh;
                background: rgba(0,0,0,0.4);
                align-items: center; justify-content: center;
            }
            #modalContent {
                background: #fff;
                padding: 20px;
                border-radius: 8px;
                max-width: 400px;
                margin: auto;
                position: relative;
            }
            #closeModal {
                position: absolute; top: 5px; right: 10px; cursor: pointer;
                font-size: 18px; color: #888;
            }
            .modal-label { display: block; margin-top: 10px; }
            .modal-input, .modal-textarea, .modal-select { width: 100%; }
            .leaflet-marker-star {
                position: absolute;
                left: 18px;
                top: -10px;
                z-index: 5000;
            }
            .star-img { width: 18px; height: 18px; }
            .edit-btn, .delete-btn {
                margin: 2px 2px 2px 0;
                padding: 2px 8px;
                font-size: 0.9em;
                cursor: pointer;
            }
            .edit-btn { background:#cfc; border: 1px solid #9c9; border-radius: 3px; }
            .delete-btn { background: #fcc; border: 1px solid #c99; border-radius: 3px; }
        </style>
    </head>
    <body>
    <button id="addSpotBtn">Add Scrumping Spot</button>
    <button id="saveSpotBtn">Save This Spot</button>
    <div id="map"></div>

    <div id="spotModal">
      <div id="modalContent">
        <span id="closeModal">&times;</span>
        <form id="spotForm">
            <input type="hidden" id="spot_id" name="spot_id">
            <label class="modal-label">Latitude:
                <input class="modal-input" type="text" id="lat" name="lat" readonly>
            </label>
            <label class="modal-label">Longitude:
                <input class="modal-input" type="text" id="lon" name="lon" readonly>
            </label>
            <label class="modal-label">Fruit (type anything):
                <input class="modal-input" type="text" id="type_of_fruit" name="type_of_fruit" required>
            </label>
            <label class="modal-label">Symbol:
                <select class="modal-select" id="symbol" name="symbol" required>
                    {% for sym in symbol_options %}
                    <option value="{{sym.value}}" data-icon="{{sym.icon}}">{{sym.label}}</option>
                    {% endfor %}
                </select>
            </label>
            <label class="modal-label">Month (scrumping time):
                <select class="modal-select" id="scrumping_month" name="scrumping_month" required>
                    {% for i in range(1,13) %}
                    <option value="{{i}}">{{["January","February","March","April","May","June","July","August","September","October","November","December"][i-1]}}</option>
                    {% endfor %}
                </select>
            </label>
            <label class="modal-label">Your Name:
                <input class="modal-input" type="text" id="your_name" name="your_name" required>
            </label>
            <label class="modal-label">Notes:
                <textarea class="modal-textarea" id="notes" name="notes"></textarea>
            </label>
            <button type="submit" id="submitSpotBtn">Add Spot</button>
            <button type="button" id="deleteSpotBtn" class="delete-btn" style="display:none;">Delete</button>
        </form>
      </div>
    </div>

    <script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>
    <script>
    const spots = {{ spots|tojson }};
    const symbolOptions = {{ symbol_options|tojson }};
    const starIcon = "{{ star_icon }}";
    const monthNames = ["January","February","March","April","May","June","July","August","September","October","November","December"];
    let markerMap = {}; // spot_id -> marker

    // --- Initialize Leaflet map ---
    const map = L.map('map').setView([{{ start_lat }}, {{ start_lon }}], 14);

    // Basemap layers
    const osm = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: 'Map data © <a href="https://openstreetmap.org">OpenStreetMap</a> contributors'
    });
    const esriSat = L.tileLayer(
        'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        {
            attribution: 'Tiles © Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'
        }
    );
    esriSat.addTo(map); // Default to satellite

    const baseMaps = {
        "Satellite": esriSat,
        "Street Map": osm
    };
    L.control.layers(baseMaps, null, {position: 'topleft'}).addTo(map);

    // --- Helper: is in season? ---
    function isInSeason(scrumping_month) {
        try {
            let now = new Date();
            let nowMonth = now.getMonth() + 1;
            let diff = Math.abs(nowMonth - parseInt(scrumping_month));
            return (diff === 0 || diff === 1 || diff === 11); // within 1 month, handle wraparound
        } catch (e) { return false; }
    }

    // --- Add existing spots as markers ---
    spots.forEach((spot, idx) => {
        let symObj = symbolOptions.find(x=>x.value===spot.symbol) || symbolOptions[0];
        let icon = L.icon({
            iconUrl: symObj.icon,
            iconSize: [32,32]
        });
        let marker = L.marker([spot.lat, spot.lon], {icon: icon}).addTo(map);

        let spot_id = spot.spot_id || idx;
        markerMap[spot_id] = marker;

        // Add star if in season
        if (isInSeason(spot.scrumping_month)) {
            let starDiv = L.divIcon({
                className: 'leaflet-marker-star',
                html: `<img class="star-img" src="${starIcon}">`,
                iconSize: [18,18],
                iconAnchor: [9,9]
            });
            let latlng = [spot.lat, spot.lon];
            L.marker(latlng, {icon: starDiv, interactive: false}).addTo(map);
        }

        let added = spot.date_added ? `<br><b>Date added:</b> ${spot.date_added}` : "";
        let fruit = spot.type_of_fruit || '';
        let monthLbl = monthNames[(spot.scrumping_month || 1)-1];
        let popup = `<b>${fruit}</b> (${monthLbl})<br>
        <b>Added by:</b> ${spot.your_name || ''}${added}<br>
        <b>Notes:</b> ${spot.notes || ''}<br>
        <button class='edit-btn' data-spotid='${spot_id}'>Edit</button>
        <button class='delete-btn' data-spotid='${spot_id}'>Delete</button>`;
        marker.bindPopup(popup);
    });

    // --- Edit/Delete handlers for popups
    map.on("popupopen", function(e) {
        let container = e.popup._contentNode;
        let editBtn = container.querySelector(".edit-btn");
        let delBtn = container.querySelector(".delete-btn");
        if (editBtn) {
            editBtn.onclick = function() {
                let spot_id = this.dataset.spotid;
                let spot = spots[spot_id];
                document.getElementById('spot_id').value = spot_id;
                document.getElementById('lat').value = spot.lat;
                document.getElementById('lon').value = spot.lon;
                document.getElementById('type_of_fruit').value = spot.type_of_fruit;
                document.getElementById('symbol').value = spot.symbol;
                document.getElementById('scrumping_month').value = spot.scrumping_month;
                document.getElementById('your_name').value = spot.your_name;
                document.getElementById('notes').value = spot.notes || "";
                document.getElementById('submitSpotBtn').innerText = "Save Changes";
                document.getElementById('deleteSpotBtn').style.display = "";
                document.getElementById('spotModal').style.display = "flex";
            };
        }
        if (delBtn) {
            delBtn.onclick = function() {
                let spot_id = this.dataset.spotid;
                if (confirm("Delete this spot?")) {
                    fetch("/delete_spot", {
                        method: "POST",
                        headers: {"Content-Type": "application/json"},
                        body: JSON.stringify({spot_id: spot_id})
                    }).then(resp => {
                        if (resp.ok) location.reload();
                        else alert("Failed to delete spot");
                    });
                }
            };
        }
    });

    // --- Add Spot Logic ---
    let addingSpot = false;
    let tempMarker = null;
    document.getElementById('addSpotBtn').onclick = function() {
        addingSpot = !addingSpot;
        this.textContent = addingSpot ? "Drag pin to location then click Save" : "Add Scrumping Spot";
        document.getElementById('saveSpotBtn').style.display = addingSpot ? "block" : "none";
        if (tempMarker) {
            map.removeLayer(tempMarker);
            tempMarker = null;
        }
        if (addingSpot) {
            let center = map.getCenter();
            let symObj = symbolOptions[0];
            let icon = L.icon({
                iconUrl: symObj.icon,
                iconSize: [32,32]
            });
            tempMarker = L.marker([center.lat, center.lng], {draggable:true, autoPan:true, icon: icon}).addTo(map);
            document.getElementById('lat').value = center.lat.toFixed(6);
            document.getElementById('lon').value = center.lng.toFixed(6);
            document.getElementById('type_of_fruit').value = "";
            document.getElementById('symbol').value = symbolOptions[0].value;
            document.getElementById('scrumping_month').value = (new Date().getMonth()+1).toString();
            document.getElementById('your_name').value = "";
            document.getElementById('notes').value = "";
            document.getElementById('spot_id').value = "";
            document.getElementById('submitSpotBtn').innerText = "Add Spot";
            document.getElementById('deleteSpotBtn').style.display = "none";
            tempMarker.on('dragend', function(e) {
                let latlng = e.target.getLatLng();
                document.getElementById('lat').value = latlng.lat.toFixed(6);
                document.getElementById('lon').value = latlng.lng.toFixed(6);
            });
        }
    };

    // When user changes symbol, update marker icon
    document.getElementById('symbol').onchange = function() {
        if (tempMarker) {
            let val = this.value;
            let symObj = symbolOptions.find(x=>x.value===val) || symbolOptions[0];
            let icon = L.icon({
                iconUrl: symObj.icon,
                iconSize: [32,32]
            });
            tempMarker.setIcon(icon);
        }
    };

    document.getElementById('saveSpotBtn').onclick = function() {
        if (tempMarker) {
            let latlng = tempMarker.getLatLng();
            document.getElementById('lat').value = latlng.lat.toFixed(6);
            document.getElementById('lon').value = latlng.lng.toFixed(6);
            document.getElementById('type_of_fruit').value = "";
            document.getElementById('symbol').value = symbolOptions[0].value;
            document.getElementById('scrumping_month').value = (new Date().getMonth()+1).toString();
            document.getElementById('your_name').value = "";
            document.getElementById('notes').value = "";
            document.getElementById('spot_id').value = "";
            document.getElementById('submitSpotBtn').innerText = "Add Spot";
            document.getElementById('deleteSpotBtn').style.display = "none";
            document.getElementById('spotModal').style.display = "flex";
        }
    };

    document.getElementById('closeModal').onclick = function() {
        document.getElementById('spotModal').style.display = "none";
        addingSpot = false;
        document.getElementById('addSpotBtn').textContent = "Add Scrumping Spot";
        document.getElementById('saveSpotBtn').style.display = "none";
        if (tempMarker) {
            map.removeLayer(tempMarker);
            tempMarker = null;
        }
    };

    document.getElementById('deleteSpotBtn').onclick = function() {
        let spot_id = document.getElementById('spot_id').value;
        if (!spot_id) return;
        if (confirm("Delete this spot?")) {
            fetch("/delete_spot", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({spot_id: spot_id})
            }).then(resp => {
                if (resp.ok) location.reload();
                else alert("Failed to delete spot");
            });
        }
    }

    document.getElementById('spotForm').onsubmit = function(e) {
        e.preventDefault();
        let spot_id = document.getElementById('spot_id').value;
        let url = spot_id !== "" ? "/edit_spot" : "/add_spot";
        let data = {
            lat: parseFloat(document.getElementById('lat').value),
            lon: parseFloat(document.getElementById('lon').value),
            type_of_fruit: document.getElementById('type_of_fruit').value,
            symbol: document.getElementById('symbol').value,
            scrumping_month: parseInt(document.getElementById('scrumping_month').value),
            your_name: document.getElementById('your_name').value,
            notes: document.getElementById('notes').value,
            spot_id: spot_id
        };
        fetch(url, {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify(data)
        }).then(resp => {
            if (resp.ok) location.reload();
            else alert("Failed to save spot");
        });
    };

    // Optional: close modal on outside click
    window.onclick = function(event) {
        let modal = document.getElementById('spotModal');
        if (event.target == modal) {
            modal.style.display = "none";
            addingSpot = false;
            document.getElementById('addSpotBtn').textContent = "Add Scrumping Spot";
            document.getElementById('saveSpotBtn').style.display = "none";
            if (tempMarker) {
                map.removeLayer(tempMarker);
                tempMarker = null;
            }
        }
    };
    </script>
    </body>
    </html>
    """, spots=[
        dict(spot, spot_id=i) for i, spot in enumerate(spots)
    ], start_lat=start_lat, start_lon=start_lon, symbol_options=SYMBOL_OPTIONS, star_icon=STAR_ICON)



@app.route("/api/spots", methods=["GET"])
def get_spots():
    spots = Spot.query.order_by(Spot.id).all()
    return jsonify([spot.to_dict() for spot in spots])


@app.route("/add_spot", methods=["POST"])
def add_spot():
    data = request.get_json()
    required = ["lat", "lon", "type_of_fruit", "symbol", "scrumping_month", "your_name"]
    if not data or not all(k in data for k in required):
        return jsonify({"error": "Invalid data"}), 400
    spots = load_spots()
    now = datetime.now().strftime('%Y-%m-%d')
    new_spot = {
        "lat": data["lat"],
        "lon": data["lon"],
        "type_of_fruit": data["type_of_fruit"],
        "symbol": data["symbol"],
        "scrumping_month": int(data["scrumping_month"]),
        "your_name": data["your_name"],
        "notes": data.get("notes", ""),
        "date_added": now
    }
    spots.append(new_spot)
    save_spots(spots)
    return jsonify({"success": True})

@app.route("/edit_spot", methods=["POST"])
def edit_spot():
    data = request.get_json()
    if "spot_id" not in data:
        return jsonify({"error": "No spot id"}), 400
    spots = load_spots()
    idx = int(data["spot_id"])
    if idx < 0 or idx >= len(spots):
        return jsonify({"error": "Invalid spot id"}), 400
    # update fields
    spots[idx]["lat"] = data["lat"]
    spots[idx]["lon"] = data["lon"]
    spots[idx]["type_of_fruit"] = data["type_of_fruit"]
    spots[idx]["symbol"] = data["symbol"]
    spots[idx]["scrumping_month"] = int(data["scrumping_month"])
    spots[idx]["your_name"] = data["your_name"]
    spots[idx]["notes"] = data.get("notes", "")
    save_spots(spots)
    return jsonify({"success": True})

@app.route("/delete_spot", methods=["POST"])
def delete_spot():
    data = request.get_json()
    if "spot_id" not in data:
        return jsonify({"error": "No spot id"}), 400
    spots = load_spots()
    idx = int(data["spot_id"])
    if idx < 0 or idx >= len(spots):
        return jsonify({"error": "Invalid spot id"}), 400
    spots.pop(idx)
    save_spots(spots)
    return jsonify({"success": True})
    
# Optional: route to delete a spot by id
@app.route("/delete_spot/<int:spot_id>", methods=["DELETE"])
def delete_spot(spot_id):
    spot = Spot.query.get(spot_id)
    if spot:
        db.session.delete(spot)
        db.session.commit()
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "error": "Spot not found"}), 404
    
if __name__ == "__main__":
    app.run(debug=True)
