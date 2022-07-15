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
    const { mode } = useColorScheme();

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

    const day = (data ? new Date(Date.parse(data.day)) : null);
    const plotlyGridColor = (mode === 'light'? '#a0a0a040' : '#40404080')
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
                                <Grid container>
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
                                    <Grid>
                                        <Typography sx={{py: 1}}>
                                            Day: {day.toLocaleDateString("en-GB", {
                                            year: 'numeric',
                                            month: 'short',
                                            day: 'numeric',
                                            weekday: 'short',
                                        })}
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
                                    data={[
                                        {
                                            x: data.chart.times,
                                            y: data.chart.half_hour_consumption,
                                            type: 'scatter',
                                            mode: 'lines',
                                            marker: {color: 'blue'},
                                        }
                                    ]}
                                    layout={{
                                        plot_bgcolor: '#00000000',
                                        paper_bgcolor: '#00000000',
                                        yaxis: { gridcolor: plotlyGridColor, },
                                        xaxis: { gridcolor: plotlyGridColor, },
                                        title: 'Consumption by half hour (kWh)',
                                        width: 800,
                                        height: 500,
                                    }}
                                />
                            </>
                            : "Loading..."
                    )}
                </Grid>
            </Grid>
            {(data && data.ok?
                <Grid container spacing={1}>
                    <Grid>
                        <Typography>
                            Daily Consumption: <NumericLabel>{data.stats.day_total}</NumericLabel> kWh
                        </Typography>
                    </Grid>
                </Grid>
                : "")}

        </>
    )
}

export default DailyConsumption;