using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Environment : MonoBehaviour
{
    struct InitTransform
    {
        public Vector3 position;
        public Quaternion rotation;
    }

    public GameObject player;
    Health playerHealth;
    InitTransform playerInit;
    public List<Health> enemiesHealth;
    List<InitTransform> enemiesInitTransform;
    // Start is called before the first frame update
    void Start()
    {
        InitEnv();
    }

    InitTransform CreateInitTransform(GameObject obj)
    {
        InitTransform initTransform;
        initTransform.position = obj.transform.position;
        initTransform.rotation = obj.transform.rotation;
        return initTransform;
    }

    void InitEnv()
    {
        playerInit = CreateInitTransform(player);
        playerHealth = player.GetComponent<Health>();
        
        enemiesHealth = new List<Health>();
        enemiesInitTransform = new List<InitTransform>();
        GameObject[] enemies = GameObject.FindGameObjectsWithTag("enemy");
        foreach(GameObject enemy in enemies)
        {
            Debug.Log("Adding enemy");
            Health enemyHealth = enemy.GetComponent<Health>();
            if (enemyHealth)
            {
                enemiesHealth.Add(enemyHealth);
                enemiesInitTransform.Add(CreateInitTransform(enemy));
            }
        }
    }

    public bool IsEpisodeTerminated()
    {
        if (playerHealth.isDead())
            return true;

        // Check if any enemies are still alive
        foreach(Health enemyHealth in enemiesHealth)
        {
            if (!enemyHealth.isDead())
            {
                return false;
            }
        }
        return true;
    }

    void ResetTransform(InitTransform init, Transform objTransform)
    {
        objTransform.position = init.position;
        objTransform.rotation = init.rotation;

    }

    void ResetEnemies()
    {
        for(int i = 0; i < enemiesHealth.Count; i++)
        {
            enemiesHealth[i].Revive();
            print(enemiesHealth[i].gameObject.name);
            ResetTransform(enemiesInitTransform[i], enemiesHealth[i].gameObject.transform);
            enemiesHealth[i].gameObject.SetActive(true);
        }
    }

    void ResetPlayer()
    {
        ResetTransform(playerInit, player.transform);
        playerHealth.Revive();
        player.SetActive(true);
    }

    public void Reset()
    {
        ResetEnemies();
        ResetPlayer();
        
    }

    // Update is called once per frame
    void Update()
    {
        // if (IsEpisodeTerminated())
        // {
        //     Reset();
        // }
    }
}
