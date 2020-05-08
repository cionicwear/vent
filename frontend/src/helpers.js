import _ from 'lodash'
import config from './config';




async function getCountyCrimeRate(counties){
  let options = {
        method: 'POST',
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({"counties": counties})
      }
      let resp = await fetch(config['backend_url'] + '/county/crime', options);
      let json =  await resp.json();
      return json
}

async function getCaliCrimeRate(){
  let options = {
        method: 'GET',
        headers: {
          "Content-Type": "application/json",
        },
      }
      let resp = await fetch(config['backend_url'] + '/california/crime', options);
      let json =  await resp.json();
      return json
}

export async function createCrimeRateGraphData(counties){
  let cali_data = await getCaliCrimeRate()
  let county_data = await getCountyCrimeRate(counties)
  var keys = Object.keys(county_data.results[0])
  var keys_filtered = keys.filter(function(value, index, arr){

  return value != 'county';

  });

  var dataX = [], dataY = [], dataCali = [];
  keys_filtered.forEach(function(item){
    dataX.push(item)
    dataY.push(county_data.results[0][item])
    dataCali.push(cali_data.results[item])
  });
  return [dataX, dataY, dataCali]

}



async function getCountyRecidivism (counties) {
    let options = {
            method: 'POST',
            headers: {
            "Content-Type": "application/json",
            },
            body: JSON.stringify({"counties": counties})
        }
        let resp = await fetch(config['backend_url'] + '/county/recidivism', options);
        let json =  await resp.json();
        json = json['results'];
        resp = {};
        json.forEach((county) => {
            let countyName = county.county;
            let c = JSON.parse(JSON.stringify(county));
            delete c.county
            resp[countyName] = c
        })
        return resp;
}

    // NOTE: this expects counties.length = 1 bc this is a hackathon and I'm bad
export async function getYearlyCountyRecidivism(counties){
    let resp = await getCountyRecidivism(counties);
    console.log(resp)
    // need aggregates from each month in last year
    for (let c of counties) {
        let agg = []
        let county = resp[c];

        Object.keys(county[config.CURRENT_YEAR]).forEach((month) => {
        if (county[config.CURRENT_YEAR][month]['Aggregate']) {

            // certified sorted
            agg.push({
            month,
            'aggregate': county[config.CURRENT_YEAR][month]['Aggregate']
            });
        }
        });

        // need 12-n months from previous year
        const nRemainingMonths = 12 - agg.length;

        let oldAgg = [];
        const lastYear = config.CURRENT_YEAR - 1

        Object.keys(county[lastYear]).forEach((month) => {
        if (county[lastYear][month]['Aggregate']) {

            // certified sorted
            oldAgg.push({
            month,
            'aggregate': county[lastYear][month]['Aggregate']
            });
        }
        });
        let remaining = _.takeRight(oldAgg, nRemainingMonths);
        const recidivismOverLastYear = remaining.concat(agg);

        let recidivismOverLastYearX = []
        let recidivismOverLastYearY = []
        for (let m of recidivismOverLastYear) {
            recidivismOverLastYearY.push(m.aggregate);
            recidivismOverLastYearX.push(m.month);
        }
        return {recidivismOverLastYearX, recidivismOverLastYearY};
    }
}

export async function getCountyRecidivismByType(counties){
  let resp = await getCountyRecidivism(counties);

  for (let c of counties) {
      let count = 0
      let h = 0;
      let prcs = 0;
      let parole = 0;
      let county = resp[c];
      let h_count = 0;
      let prcs_count = 0;
      let parole_count = 0;

      Object.keys(county[config.CURRENT_YEAR]).forEach((month) => {
      if (county[config.CURRENT_YEAR][month]['1170(h)']) {
          h += county[config.CURRENT_YEAR][month]['1170(h)']
          h_count +=1
      }
      if (county[config.CURRENT_YEAR][month]['PRCS']) {
          prcs += county[config.CURRENT_YEAR][month]['PRCS']
          prcs_count +=1
      }
      if (county[config.CURRENT_YEAR][month]['Parolees']) {
          parole += county[config.CURRENT_YEAR][month]['Parolees']
          parole_count += 1
      }
      count += 1
      });

      // Sorry said fuck it to the wrap aroudn cuz i was just doing coutns and its 10 months
      const nRemainingMonths = 12 - (count-1);

      // const lastYear = config.CURRENT_YEAR - 1
      // Object.keys(county[lastYear]).forEach((month) => {
      // if (county[lastYear][month]['1170(h)']) {
      //   h += county[lastYear][month]['1170(h)']
      // }
      // if (county[lastYear][month]['PRCS']) {
      //   prcs += county[lastYear][month]['PRCS']
      // }
      // if (county[lastYear][month]['Parolees']) {
      //   parole += county[lastYear][month]['Parolees']
      // }
      // });

      let labelsX = ["1170h", "PRCS", "Parolees"]
      let dataY = [h, prcs, parole]

      return [labelsX, dataY];
  }


}
