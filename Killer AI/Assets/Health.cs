using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public class Health : MonoBehaviour
{   
    [HideInInspector]
    public float health;
    public bool shouldSetActive = true;

    public float maxHealth; 
    Slider healthSlider;
    // Start is called before the first frame update
    void Awake()
    {
        healthSlider = GetComponentInChildren<Slider>();
        health = maxHealth;
    }
    public void Revive()
    {
        health = maxHealth;
        healthSlider.value = 1.0f;
    }

    public void Damage(float hitPoints)
    {
        health -= hitPoints;

        healthSlider.value = Mathf.Max(health/maxHealth, 0.0f);
        if (health <= 0.0f)
        {
            Death();
        }
    }

    public bool isDead()
    {
        return health <= 0.0f;
    }

    void Death()
    {
        if (shouldSetActive)
        {
            gameObject.SetActive(false);
        }
        
    }
}
