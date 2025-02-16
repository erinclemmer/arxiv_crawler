import axios from "axios"
import qs from 'qs'

const host = window.location.host.split(':')[0]

export async function getApi(path: string, data: any = null) {
    return data == null 
        ? await axios.get(`http://${host}:4000/api/${path}`)
        : await axios.get(`http://${host}:4000/api/${path}?${qs.stringify(data)}`)
}

export async function postApi(path: string, data: any = { }) {
    return await axios.post(`http://${host}:4000/api/${path}`, data)
}

export async function download(url: string, data: any = { }) {
    return new Promise(async (res: any, rej: any) => {
        const response = await axios({
            method: 'get',
            url: `http://${host}:4000/api/${url}?${qs.stringify(data)}`,
            responseType: 'stream',
        })
        const objectUrl = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a')
        if (link == null) {
            rej()
            return
        }
        link.href = objectUrl
        link.setAttribute('download', 'tune.jsonl');
        document.body.appendChild(link)
        link.click()

        if (link.parentNode != null) {
            link.parentNode.removeChild(link);
        }
        res()
    })
}