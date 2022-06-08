using System.Collections;
using System.Collections.Generic;
using UnityEngine;
public class State {
    public float[] position = new float[3];
    public float[] rotation = new float[4];

    public float health;

    public List<EnemyState> enemies = new List<EnemyState>();

    // public State Clone()
    // {
    //     State cloneState = new State();
    //     cloneState.position = position.Clone();
    //     cloneState.rotation = rotation.Clone();
        
    //     foreach(EnemyState enemy in enemies)
    //     {
    //         EnemyState enemyState = new EnemyState();
    //         enemyState.position = enemy.position.Clone();
    //         enemyState.rotation = enemy.rotation.Clone();
    //         cloneState.enemies.Add(enemyState);
    //     }
    //     return cloneState;
    // }
}

public class EnemyState
{
    public float[] position = new float[3];
    public float[] rotation = new float[4];
    public float health;
}

public class RecordPlayer : MonoBehaviour
{


    public Environment env;
    public int tickRecordFreq = 4;
    public int curTick = 0;
    PlayerMovement playerMovement;
    Health playerHealth;
    private PolicyConnectionShooting policyCon;
    int elapsedEpisodes = 0;
    bool shouldReset;
    bool doReset;

    List<State> states = new List<State>();
    List<Action> actions = new List<Action>();
    List<float> rewards = new List<float>();
    
    // Start is called before the first frame update
    void Start()
    {
        playerMovement = GetComponent<PlayerMovement>();
        policyCon = GetComponent<PolicyConnectionShooting>();
        playerHealth = GetComponent<Health>();
        Connect();

    }
    // Update is called once per frame
    void LateUpdate()
    {
        if (doReset)
        {
            env.Reset();
            doReset = false;
            curTick = 0;
        }
        else if (env.IsEpisodeTerminated() && !shouldReset)
        {
            elapsedEpisodes += 1;
            shouldReset = true;
            SendEpisode();
        }
        else if (!shouldReset)
        {
            if (curTick % tickRecordFreq == 0)
            {
                RecordAction();
                RecordState();
            }

            curTick += 1;
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
        float reward = 0.0f;
        State state = new State();
        RecordTransform(state.position, state.rotation, transform);  
        for(int i = 0; i < env.enemiesHealth.Count; i++)
        {
            EnemyState enemyState = new EnemyState();
            RecordTransform(enemyState.position, enemyState.rotation, env.enemiesHealth[i].transform);
            enemyState.health = env.enemiesHealth[i].health;
            

            if (states.Count > 0)
            {
                reward +=  states[states.Count - 1].enemies[i].health - enemyState.health;
            }
            state.enemies.Add(enemyState);
        }
        state.health = playerHealth.health; 
        if (states.Count > 0)
        {
            reward += state.health - states[states.Count - 1].health;
        }
        states.Add(state);
        rewards.Add(reward);
    }

    private void RecordAction()
    {
        playerMovement.action.Print();
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
        stateDict["rewards"] = rewards;

        policyCon.isEpisodeOver = true;
        policyCon.SendState(stateDict);
    }

    private void Reset()
    {
        states = new List<State>();
        actions = new List<Action>();
        rewards = new List<float>();
        doReset = true;
        shouldReset = false;
    }   
}
