import {useEffect, useState} from "react";
import {useColorScheme} from "@mui/joy/styles";
import Typography from '@mui/joy/Typography';
import Button from "@mui/joy/Button";
import {Grid} from "@mui/joy";
import NumericLabel from "react-pretty-numbers"
import Plot from 'react-plotly.js';

function DailyConsumption() {
    let [data, setData] = useState(null)
    let [dayToGet, setDayToGet] = useState('last')
    const {mode} = useColorScheme();

    useEffect(() => {
        fetch('/chart/daily/' + dayToGet)
            .then(response => response.json())
            .then(data => {
                console.log(data);
                setData(data);
            });
    }, [dayToGet])

    const changeDay = (forward) => {
        if (!data) return;
        if (forward && !data.meta.next) return;
        if (!forward && !data.meta.prev) return;
        setDayToGet((forward ? data.meta.next : data.meta.prev))
    }

    const day = (data && data.ok ? new Date(Date.parse(data.day)) : null);
    const chartData = (!data || !data.ok ? null :
            (data.chart.base_load ?
                    [
                        {
                            x: data.chart.times,
                            y: data.chart.base_load,
                            fill: 'tonexty',
                            type: 'scatter',
                            mode: 'none',
                            name: 'base load',
                        },
                        {
                            x: data.chart.times,
                            y: data.chart.half_hour_consumption,
                            fill: 'tonexty',
                            type: 'scatter',
                            mode: 'none',
                            name: 'full load'
                        }
                    ]
                    :
                    [
                        {
                            x: data.chart.times,
                            y: data.chart.half_hour_consumption,
                            type: 'bar',
                        }
                    ]
            )
    )
    const plotlyGridColor = (mode === 'light' ? '#a0a0a040' : '#40404080')
    return (
        <>
            <Grid container spacing={1}>
                <Grid>
                    <Typography level="h3" component="h3">
                        Daily Consumption Analysis
                    </Typography>
                </Grid>
            </Grid>
            <Grid container spacing={1}>
                <Grid width={800} height={600}>
                    {(data && !data.ok ?
                        <Typography>
                            Error: {data.error}
                        </Typography>
                        : "")}
                    {(data && data.ok ?
                            <>
                                <Grid container alignItems="center" justifyContent="center">
                                    <Grid item xs={1}>
                                        <Button
                                            onClick={() => setDayToGet(data.meta.first_full_day)}
                                        >
                                            First
                                        </Button>
                                    </Grid>
                                    <Grid item xs={1}>

                                        <Button
                                            disabled={data.meta.prev === null}
                                            onClick={() => changeDay(false)}
                                        >
                                            Prev
                                        </Button>
                                    </Grid>
                                    <Grid width={180} textAlign="center">
                                        <Typography sx={{py: 1}}>
                                            <b>{day.toLocaleDateString("en-GB", {
                                                year: 'numeric',
                                                month: 'short',
                                                day: 'numeric',
                                                weekday: 'short',
                                            })}</b>
                                        </Typography>
                                    </Grid>
                                    <Grid item xs={1}>
                                        <Button
                                            disabled={data.meta.next === null}
                                            onClick={() => changeDay(true)}
                                        >
                                            Next
                                        </Button>
                                    </Grid>
                                    <Grid item xs={1}>
                                        <Button
                                            onClick={() => setDayToGet(data.meta.last_full_day)}
                                        >
                                            Last
                                        </Button>
                                    </Grid>
                                </Grid>
                                <Plot
                                    data={chartData}
                                    layout={{
                                        plot_bgcolor: '#00000000',
                                        paper_bgcolor: '#00000000',
                                        yaxis: {
                                            range: [data.meta.min, data.meta.max],
                                            gridcolor: plotlyGridColor,
                                        },
                                        xaxis: {
                                            gridcolor: plotlyGridColor,
                                        },
                                        title: 'Consumption by half hour (kWh)',
                                        width: 800,
                                        height: 500,
                                    }}
                                />
                                <Typography textAlign="center" level="body1">
                                    Total: <b><NumericLabel>{data.stats.day_total}</NumericLabel></b> kWh
                                    {(data.stats.base_load_total ?
                                        <>
                                            &nbsp;| Base load: <NumericLabel>{data.stats.base_load_total}</NumericLabel> kWh
                                        </>
                                    : "")}
                                    {(data.stats.is_full_day ? "" :
                                            <span style={{color: "red"}}><b>
                                                &nbsp; incomplete data
                                            </b></span>
                                    )}
                                </Typography>
                                <Typography textAlign="center" level="body3">
                                    {(data.stats.is_full_day ? "" :
                                                <>
                                                    As this day doesn't have a full dataset,
                                                    it is ignored in the analycis.
                                                </>
                                    )}
                                    {(data.chart.base_load ?
                                        <>
                                            The chart shows the running average base load from   the
                                            previous {data.meta.base_load_days} days
                                            with the variable consumption on top.&nbsp;
                                        </>
                                        : "")}
                                    Days start at: {data.meta.new_day_start}.
                                </Typography>
                            </>
                            : "Loading..."
                    )}
                </Grid>
            </Grid>
        </>
    )
}

export default DailyConsumption;