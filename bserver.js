const bleno = require("bleno");

console.log(`node v: ${process.version}`);

const name = "ionboard";
const START_ADVERTISING_UUID = "3abf2f10-171b-4c93-b1df-3c7f6b687e52";
const SERVICE_UUID = "3abf2f10-171b-4c93-b1df-3c7f6b687e53";
const CHARACTERISTIC_UUID = "3abf2f10-171b-4c93-b1df-3c7f6b687e54"


let updateValue;

const coreCharacteristic = new bleno.Characteristic({
								uuid: CHARACTERISTIC_UUID,
								properties: ["read", "write", "notify", "indicate"],
								secure: [],
								descriptors: [],
								onSubscribe: (maxValueSize, updateValueCallback) => {
										console.log("Client Subscribed");
										updateValue = updateValueCallback;
										const data = Buffer.from("wasson client", "utf8");		
										updateValueCallback(data);
									},
								onUnsubscribe: () => {
										console.log("unsubscribe");
										updateValue = null;
									},
								onWriteRequest: (data, offset, withResponse, callback) => {
										console.log(data.toString("utf8"));
										callback(this.RESULT_SUCCESS);
									},							
							})				


bleno.on("stateChange", (state) => {
	console.log("on -> stateChange: " + state);
	
	if(state === "poweredOn") {
		bleno.startAdvertising(name, [START_ADVERTISING_UUID]);
	}
	else {
		bleno.stopAdvertising();
	}
	
});

const sendMessageToClients = (message) => {
	if (updateValue) {
		const data = Buffer.from(message, "utf8");		
		updateValue(data);
	}
	else {
		console.error("No subscribed clients");
	}
}

setInterval(()=>{
		sendMessageToClients("wasson client");
	}, 2000);



bleno.on("advertisingStart", (error) => {
	console.log("on -> advertisingStart: " + (error ? "error " + error : "success"));
	
	if (!error) {
		bleno.setServices([
			new bleno.PrimaryService({
				uuid: SERVICE_UUID,
				characteristics: [
					coreCharacteristic
				]
				})
		])
	}
	
});
