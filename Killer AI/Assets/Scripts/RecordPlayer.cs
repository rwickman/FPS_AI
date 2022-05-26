using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class RecordPlayer : MonoBehaviour
{
    public class State {
        public float[] position = new float[3];
        public float[] rotation = new float[4];

        public List<EnemyState> enemies = new List<EnemyState>();
    }

    public class EnemyState
    {
        public float[] position = new float[3];
        public float[] rotation = new float[4];
    }

    public Environment env;
    PlayerMovement playerMovement;
    private PolicyConnectionShooting policyCon;
    int elapsedEpisodes = 0;
    bool shouldReset;

    List<State> states = new List<State>();
    List<Action> actions = new List<Action>();
    
    // Start is called before the first frame update
    void Start()
    {
        playerMovement = GetComponent<PlayerMovement>();
        policyCon = GetComponent<PolicyConnectionShooting>();
        Connect();

    }
    // Update is called once per frame
    void LateUpdate()
    {
        if (env.IsEpisodeTerminated() && !shouldReset)
        {
            elapsedEpisodes += 1;
            shouldReset = true;
            SendEpisode();
        }
        else if (!shouldReset)
        {
            RecordAction();
            RecordState();
        }
    }

    void RecordTransform(float[] pos, float[] rot, Transform objTransform)
    {
        pos[0] = objTransform.position.x;
        pos[1] = objTransform.position.y;
        pos[2] = objTransform.position.z;

        rot[0] = objTransform.rotation.x;
        rot[1] = objTransform.rotation.y;
        rot[2] = objTransform.rotation.z;
        rot[3] = objTransform.rotation.w;
    }

    private void RecordState()
    {
        State state = new State();
        RecordTransform(state.position, state.rotation, transform);  
        foreach(Health enemyHealth in env.enemiesHealth)
        {
            EnemyState enemyState = new EnemyState();
            RecordTransform(enemyState.position, enemyState.rotation, enemyHealth.transform);
            state.enemies.Add(enemyState);
        }

        states.Add(state);
    }

    private void RecordAction()
    {
        // playerMovement.action.Print();
        actions.Add(playerMovement.action);
    }

    private void Connect()
    {   
        policyCon.StartConnection(Reset);
    }

    private void SendEpisode()
    {
        Dictionary<string, dynamic> stateDict = new Dictionary<string, dynamic>();
        stateDict["states"] = states;
        stateDict["actions"] = actions;

        policyCon.isEpisodeOver = true;
        policyCon.SendState(stateDict);
    }

    private void Reset()
    {
        env.Reset();
        shouldReset = false;
    }   
}
