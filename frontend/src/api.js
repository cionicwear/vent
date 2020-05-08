import config from './config';

export async function getSensorData(count){
  let options = {
        method: 'GET',
        headers: {
          "Content-Type": "application/json",
        },
      }
      
      // var url = new URL('/sensors')
      // var params = { count }
      // url.search = new URLSearchParams(params).toString();
      // console.log(url);
      let resp = await fetch('/sensors?count=1', options);
      let json =  await resp.json();
      return json
}
