using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Gun : MonoBehaviour
{
    // Start is called before the first frame update
    public GameObject bullet;
    public Transform gunOffset;
    
    public float bulletForce = 100f;

    public float shotDelay = 0.5f;
    
    [HideInInspector]
    public float lastTimeShot = 0.0f;
    
    public void Shoot()
    {
        if (Time.time - lastTimeShot > shotDelay)
        {
            lastTimeShot = Time.time;
            GameObject bulletFired = Instantiate(bullet, gunOffset.position, transform.rotation);
            bulletFired.transform.Rotate(0.0f, -90.0f, 0.0f);
            bulletFired.GetComponent<Rigidbody>().AddForce(transform.forward * bulletForce);
        }
    }
}
