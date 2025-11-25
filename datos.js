[
{{repeat(1000)}},
{
_id: '{{objectId()}}',

player: '{{firstName()}} {{surname()}}',
sport: '{{random("football", "basketball", "soccer", "tennis", "hockey")}}',

/* -------------------------
   MARKOV CHAIN - PERFORMANCE STATES
   ------------------------- */
performanceState: '{{random("peak", "good", "average", "declining", "injured")}}',
previousPerformanceState: '{{random("peak", "good", "average", "declining")}}',
stateTransitionProb: '{{floating(0.0, 1.0, 3, "0.000")}}',
timeInPerformanceState: '{{integer(5, 300)}}',
expectedPerformanceDuration: '{{integer(10, 180)}}',

/* -------------------------
   SENSOR PERFORMANCE METRICS
   ------------------------- */
performanceData: {
  speed: '{{floating(5, 30, 2, "0.00")}} m/s',
  accuracy: '{{integer(50, 100)}}%',
  stamina: '{{integer(0, 100)}}%',
  consistency: '{{floating(0.0, 1.0, 2, "0.00")}}',
  pressureHandling: '{{floating(0.0, 1.0, 2, "0.00")}}'
},

/* -------------------------
   GAME FLOW ANALYSIS
   ------------------------- */
gameFlowAnalysis: {
  momentumState: '{{random("strong_favor", "slight_favor", "neutral", "slight_against", "strong_against")}}',
  momentumTransitionProb: '{{floating(0.0, 1.0, 3, "0.000")}}',
  scoringProbability: '{{floating(0.0, 1.0, 3, "0.000")}}',
  gamePhase: '{{random("opening", "early", "middle", "late", "critical")}}'
},

/* -------------------------
   TEAM DYNAMICS
   ------------------------- */
teamDynamics: {
  teamState: '{{random("coordinated", "average", "disjointed")}}',
  roleInTeam: '{{random("leader", "supporting", "specialist", "substitute")}}',
  teamChemistry: '{{floating(0.0, 1.0, 2, "0.00")}}',
  communicationEffectiveness: '{{floating(0.0, 1.0, 2, "0.00")}}'
},

/* -------------------------
   STRATEGIC ANALYSIS
   ------------------------- */
strategicAnalysis: {
  optimalStrategy: '{{random("aggressive", "defensive", "balanced", "adaptive")}}',
  strategyTransitionProb: '{{floating(0.0, 1.0, 3, "0.000")}}',
  counterStrategyRisk: '{{floating(0.0, 1.0, 2, "0.00")}}',
  adaptabilityIndex: '{{floating(0.0, 1.0, 2, "0.00")}}'
},

/* -------------------------
   PERFORMANCE PREDICTION (Markov + Stats)
   ------------------------- */
performancePrediction: {
  nextGamePerformance: '{{random("peak", "good", "average", "declining")}}',
  predictionConfidence: '{{floating(0.0, 1.0, 2, "0.00")}}',
  expectedImprovement: '{{floating(-20.0, 50.0, 1, "0.0")}}',
  recoveryTime: '{{integer(24, 720)}}'
},

/* -------------------------
   INJURY RISK ANALYSIS
   ------------------------- */
injuryRiskAnalysis: {
  currentRiskLevel: '{{floating(0.0, 1.0, 2, "0.00")}}',
  injuryTransitionProb: '{{floating(0.0, 0.1, 4, "0.0000")}}',
  recoveryStateProb: '{{floating(0.0, 1.0, 3, "0.000")}}',
  fitnessDeclineRate: '{{floating(0.0, 0.1, 4, "0.0000")}}'
},

/* -------------------------
   BLOOM FILTER + MINWISE + HLL + DGIM FIELDS
   ------------------------- */
playType: '{{random("offensive", "defensive", "special", "transition")}}',
performancePeak: '{{bool()}}',
stationaryPerformance: '{{floating(0.0, 1.0, 3, "0.000")}}',
ergodicity: '{{bool()}}',
mixingTime: '{{integer(10, 120)}}',

/* -------------------------
   MAPREDUCE EXTENSIONS (Group 11 - Unit 4)
   ------------------------- */
mapReducePartition: '{{integer(1, 22)}}',
processingNode: 'node_{{integer(1, 11)}}',
batchId: 'batch_{{integer(1000, 9999)}}',
aggregationKey: '{{performanceState}}_{{sport}}',

/* -------------------------
   FINAL TIMESTAMP
   ------------------------- */
timestamp: '{{date(new Date(), "YYYY-MM-ddThh:mm:ss Z")}}'
}
]
