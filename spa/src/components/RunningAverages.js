import {useEffect, useState} from "react";
import {useColorScheme} from "@mui/joy/styles";
import Typography from '@mui/joy/Typography';
import Button from "@mui/joy/Button";
import {Grid} from "@mui/joy";
import Plot from 'react-plotly.js';

function RunningAverages() {
    let [data, setData] = useState(null)
    let [whichKind, setWhichKind] = useState('total')
    const {mode} = useColorScheme();

    useEffect(() => {
        fetch('/chart/averages/' + whichKind)
            .then(response => response.json())
            .then(data => {
                console.log(data);
                setData(data);
            });
    }, [whichKind])

    const plotlyGridColor = (mode === 'light' ? '#a0a0a040' : '#40404080')
    const plotlyCharts = []
    if (data && data.ok)
        for (let a in data.chart)
            if (a !== 'days')
                plotlyCharts.push({
                    x: data.chart.days,
                    y: data.chart[a],
                    type: 'scatter',
                    mode: 'lines',
                    name: a,
                })
    const title = (() => {
        switch (whichKind) {
            case 'total':
                return "Average Total Daily Consumption"
            case 'base':
                return "Average Baase Load"
            case 'max':
                return "Average Maximum Half-hourly Consumption"
        }
    })();

    return (
        <>
            <Grid container spacing={1}>
                <Grid>
                    <Typography level="h3" component="h3">
                        Running Average Consumption Analysis
                    </Typography>
                </Grid>
            </Grid>
            <Grid container spacing={1}>
                <Grid>
                    <Button
                        disabled={whichKind === 'total'}
                        onClick={() => setWhichKind('total')}
                    >
                        Total
                    </Button>
                </Grid>
                <Grid>
                    <Button
                        disabled={whichKind === 'base'}
                        onClick={() => setWhichKind('base')}
                    >
                        Base Load
                    </Button>
                </Grid>
                <Grid>
                    <Button
                        disabled={whichKind === 'max'}
                        onClick={() => setWhichKind('max')}
                    >
                        Max
                    </Button>
                </Grid>
                <Grid sx={{px: 3}}>
                    <Typography sx={{py: 1}}>
                        <b>{title}</b>
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
                                <Plot
                                    data={plotlyCharts}
                                    layout={{
                                        plot_bgcolor: '#00000000',
                                        paper_bgcolor: '#00000000',
                                        yaxis: {gridcolor: plotlyGridColor,},
                                        xaxis: {gridcolor: plotlyGridColor,},
                                        title: 'Running Averages (kWh)',
                                        width: 800,
                                        height: 500,
                                    }}
                                />
                            </>
                            : "Loading..."
                    )}
                </Grid>
            </Grid>
        </>
    )
}

export default RunningAverages;