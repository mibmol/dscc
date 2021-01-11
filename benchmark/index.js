const autocannon = require('autocannon')
const fs = require('fs')

const N_ROWS = 500000

function randomInt(min = 0, max = 12) {
	if(max > Number.MAX_SAFE_INTEGER){
		max = Number.MAX_SAFE_INTEGER
	}
	return Math.floor(Math.random() * max) + min
}

function getRandomPath() {
	return `/company/station/${randomInt(2, N_ROWS)}/`
}

function makeReq(n) {
	let reqs = []
	let count = n
	while (--count > 0) {
		reqs.push({
			method: 'GET',
			path: getRandomPath(),
		})
	}
	console.log(reqs[200], reqs.length)
	return reqs
}

function saveToFile(err, { latency, requests, throughput }) {
	let metrics = [
		`${N_ROWS}:`,
		`lat: ${latency.average} ms`,
		`req/s: ${requests.average}`,
		`throughput: ${throughput.average/1000} KB/s`,
	]

	fs.appendFile("./monolit_cache_docker.txt", `${metrics.join('\t')}\n`, (err) => {
		if (err) {
			console.error(err)
		}
		console.log(metrics.join('\t'))
	})
}

autocannon({
	url: 'http://localhost:80',
	connections: 32,
	duration: 12,
	requests: makeReq(Math.floor(90000))
}, saveToFile)

